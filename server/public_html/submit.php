<?php

declare(strict_types=1);

use PHPMailer\PHPMailer\Exception as MailException;
use PHPMailer\PHPMailer\PHPMailer;

const FIELD_LIMIT = 2000;
const SHORT_FIELD_LIMIT = 300;

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
header('X-Content-Type-Options: nosniff');
header('Referrer-Policy: no-referrer');

$root = dirname(__DIR__);
$configFile = $root . '/config.php';
$autoloadFile = $root . '/vendor/autoload.php';

if (!is_file($configFile) || !is_file($autoloadFile)) {
    error_log('UrbanFresh RFQ mailer is not configured.');
    respond(503, ['ok' => false, 'error' => 'Email service is temporarily unavailable.']);
}

/** @var array<string, mixed> $config */
$config = require $configFile;
require $autoloadFile;

$origin = isset($_SERVER['HTTP_ORIGIN']) ? trim((string) $_SERVER['HTTP_ORIGIN']) : '';
$site = siteProfile($origin);
$originAllowed = $site !== null;

if ($originAllowed) {
    header('Access-Control-Allow-Origin: ' . $origin);
    header('Vary: Origin');
    header('Access-Control-Allow-Methods: POST, OPTIONS');
    header('Access-Control-Allow-Headers: Content-Type, Accept');
    header('Access-Control-Max-Age: 600');
}

if (($_SERVER['REQUEST_METHOD'] ?? '') === 'OPTIONS') {
    if (!$originAllowed) {
        respond(403, ['ok' => false, 'error' => 'Origin is not allowed.']);
    }
    respond(204, []);
}

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    header('Allow: POST, OPTIONS');
    respond(405, ['ok' => false, 'error' => 'Method not allowed.']);
}

if (!$originAllowed) {
    respond(403, ['ok' => false, 'error' => 'Origin is not allowed.']);
}

$data = requestData();

if (clean($data['website'] ?? '', SHORT_FIELD_LIMIT) !== '') {
    respond(200, ['ok' => true]);
}

$fields = [
    'name' => clean($data['name'] ?? '', SHORT_FIELD_LIMIT),
    'phone' => clean($data['phone'] ?? '', SHORT_FIELD_LIMIT),
    'email' => clean($data['email'] ?? '', SHORT_FIELD_LIMIT),
    'buyer_type' => clean($data['buyer_type'] ?? '', SHORT_FIELD_LIMIT),
    'location' => clean($data['location'] ?? '', SHORT_FIELD_LIMIT),
    'variety' => clean($data['variety'] ?? '', SHORT_FIELD_LIMIT),
    'processing' => clean($data['processing'] ?? '', SHORT_FIELD_LIMIT),
    'quantity' => clean($data['quantity'] ?? '', SHORT_FIELD_LIMIT),
    'packaging' => clean($data['packaging'] ?? '', SHORT_FIELD_LIMIT),
    'timeline' => clean($data['timeline'] ?? '', SHORT_FIELD_LIMIT),
    'message' => clean($data['message'] ?? '', FIELD_LIMIT),
    'source_page' => clean($data['source_page'] ?? '', FIELD_LIMIT),
    'lead_id' => clean($data['lead_id'] ?? '', SHORT_FIELD_LIMIT),
];

foreach (['name', 'phone', 'email', 'location', 'quantity'] as $required) {
    if ($fields[$required] === '') {
        respond(422, ['ok' => false, 'error' => 'Please complete every required field.']);
    }
}

if (!filter_var($fields['email'], FILTER_VALIDATE_EMAIL)) {
    respond(422, ['ok' => false, 'error' => 'Please enter a valid business email.']);
}

if (!rateLimit($root . '/var', clientAddress(), (int) ($config['rate_limit_per_hour'] ?? 6))) {
    respond(429, ['ok' => false, 'error' => 'Too many requests. Please try again later.']);
}

$leadId = $fields['lead_id'] !== '' ? $fields['lead_id'] : bin2hex(random_bytes(16));
$safeLeadId = preg_replace('/[^a-zA-Z0-9_-]/', '', $leadId) ?: bin2hex(random_bytes(16));

try {
    sendOwnerNotification($config, $fields, $safeLeadId, $site);
    sendBuyerConfirmation($config, $fields, $safeLeadId, $site);
    respond(200, ['ok' => true, 'lead_id' => $safeLeadId]);
} catch (Throwable $error) {
    error_log(sprintf(
        'UrbanFresh RFQ email failed for lead %s: %s',
        $safeLeadId,
        $error->getMessage()
    ));
    respond(502, ['ok' => false, 'error' => 'We could not send the email confirmation. Please use WhatsApp or try again.']);
}

/**
 * @return array<string, mixed>
 */
function requestData(): array
{
    $contentType = isset($_SERVER['CONTENT_TYPE']) ? strtolower((string) $_SERVER['CONTENT_TYPE']) : '';
    if (strpos($contentType, 'application/json') === 0) {
        $decoded = json_decode((string) file_get_contents('php://input'), true);
        return is_array($decoded) ? $decoded : [];
    }
    return $_POST;
}

/**
 * @param mixed $value
 */
function clean($value, int $limit): string
{
    $text = trim((string) $value);
    return function_exists('mb_substr') ? mb_substr($text, 0, $limit) : substr($text, 0, $limit);
}

function clientAddress(): string
{
    foreach (['HTTP_CF_CONNECTING_IP', 'HTTP_X_FORWARDED_FOR', 'REMOTE_ADDR'] as $key) {
        if (!empty($_SERVER[$key])) {
            return trim(explode(',', (string) $_SERVER[$key])[0]);
        }
    }
    return 'unknown';
}

function rateLimit(string $varDirectory, string $address, int $maximum): bool
{
    if ($maximum < 1) {
        return false;
    }
    if (!is_dir($varDirectory) && !mkdir($varDirectory, 0700, true) && !is_dir($varDirectory)) {
        throw new RuntimeException('Unable to initialize rate limiting.');
    }

    $bucket = gmdate('YmdH');
    $path = $varDirectory . '/rate-' . hash('sha256', $address . '|' . $bucket) . '.json';
    $handle = fopen($path, 'c+');
    if ($handle === false || !flock($handle, LOCK_EX)) {
        throw new RuntimeException('Unable to apply rate limiting.');
    }

    $stored = stream_get_contents($handle);
    $count = $stored !== false && $stored !== '' ? (int) $stored : 0;
    if ($count >= $maximum) {
        flock($handle, LOCK_UN);
        fclose($handle);
        return false;
    }

    ftruncate($handle, 0);
    rewind($handle);
    fwrite($handle, (string) ($count + 1));
    fflush($handle);
    flock($handle, LOCK_UN);
    fclose($handle);
    @chmod($path, 0600);
    return true;
}

/**
 * @return array<string, string>|null
 */
function siteProfile(string $origin): ?array
{
    if (in_array($origin, ['https://urbanfresh.in', 'https://www.urbanfresh.in'], true)) {
        return [
            'site' => 'urbanfresh.in',
            'owner_subject' => 'New domestic rice quote request',
            'owner_heading' => 'New domestic rice quote request',
            'buyer_intro' => 'Thank you for sending your bulk rice quote request to UrbanFresh Rice Mills. Our buyer desk will review the product, quantity, packing, delivery location and timeline you provided.',
            'location_label' => 'Delivery city or country',
            'notes_label' => 'Other requirements',
            'desk_label' => 'Buyer desk',
        ];
    }

    if (in_array($origin, ['https://urbanfreshrice.com', 'https://www.urbanfreshrice.com'], true)) {
        return [
            'site' => 'urbanfreshrice.com',
            'owner_subject' => 'New international rice RFQ',
            'owner_heading' => 'New international rice RFQ',
            'buyer_intro' => 'Thank you for sending your international rice requirement to UrbanFresh Rice Mills. Our buyer desk will review the product, quality, packing, destination and shipment details you provided.',
            'location_label' => 'Destination country / port',
            'notes_label' => 'Specification and notes',
            'desk_label' => 'International buyer desk',
        ];
    }

    return null;
}

/**
 * @param array<string, mixed> $config
 * @param array<string, string> $fields
 * @param array<string, string> $site
 */
function sendOwnerNotification(array $config, array $fields, string $leadId, array $site): void
{
    $mail = configuredMailer($config);
    $mail->addAddress((string) $config['notification_email'], (string) $config['notification_name']);
    $mail->addReplyTo($fields['email'], $fields['name']);
    $mail->Subject = $site['owner_subject'] . ' — ' . subjectText($fields['name']);
    $mail->isHTML(true);
    $mail->Body = emailShell(
        $site['owner_heading'],
        '<p>A buyer submitted a structured request through ' . escapeHtml($site['site']) . '.</p>' .
        detailsTable($fields, $leadId, $site) .
        '<p style="margin:24px 0 0"><strong>Reply directly to this email</strong> to contact the buyer.</p>',
        $site
    );
    $mail->AltBody = ownerPlainText($fields, $leadId, $site);
    $mail->send();
}

/**
 * @param array<string, mixed> $config
 * @param array<string, string> $fields
 * @param array<string, string> $site
 */
function sendBuyerConfirmation(array $config, array $fields, string $leadId, array $site): void
{
    $mail = configuredMailer($config);
    $mail->addAddress($fields['email'], $fields['name']);
    $mail->addReplyTo((string) $config['notification_email'], (string) $config['notification_name']);
    $mail->Subject = 'We received your rice RFQ — UrbanFresh';
    $mail->isHTML(true);
    $mail->Body = emailShell(
        'Your rice request has been received',
        '<p>Hello ' . escapeHtml($fields['name']) . ',</p>' .
        '<p>' . escapeHtml($site['buyer_intro']) . '</p>' .
        '<p>This confirmation records your request; commercial feasibility, specification acceptance and terms remain subject to written review.</p>' .
        detailsTable($fields, $leadId, $site) .
        '<p style="margin:24px 0 0">To add documents or more details, reply to this email or continue on WhatsApp at <a href="https://wa.me/919433569217" style="color:#1f6b4f">+91 94335 69217</a>.</p>',
        $site
    );
    $mail->AltBody = buyerPlainText($fields, $leadId, $site);
    $mail->send();
}

/**
 * @param array<string, mixed> $config
 */
function configuredMailer(array $config): PHPMailer
{
    $smtp = isset($config['smtp']) && is_array($config['smtp']) ? $config['smtp'] : [];
    $mail = new PHPMailer(true);
    $mail->isSMTP();
    $mail->Host = (string) ($smtp['host'] ?? 'smtp.hostinger.com');
    $mail->SMTPAuth = true;
    $mail->Username = (string) ($smtp['username'] ?? '');
    $mail->Password = (string) ($smtp['password'] ?? '');
    $mail->Port = (int) ($smtp['port'] ?? 587);
    $mail->SMTPSecure = (string) ($smtp['encryption'] ?? PHPMailer::ENCRYPTION_STARTTLS);
    $mail->CharSet = PHPMailer::CHARSET_UTF8;
    $mail->Timeout = 15;
    $mail->setFrom((string) $config['from_email'], (string) $config['from_name']);
    return $mail;
}

/**
 * @param array<string, string> $fields
 * @param array<string, string> $site
 */
function detailsTable(array $fields, string $leadId, array $site): string
{
    $rows = [
        'Name or company' => $fields['name'],
        'Phone / WhatsApp' => $fields['phone'],
        'Business email' => $fields['email'],
        $site['location_label'] => $fields['location'],
        'Buyer type' => fallback($fields['buyer_type']),
        'Rice variety' => fallback($fields['variety'], 'Please advise'),
        'Processing' => fallback($fields['processing'], 'Please advise'),
        'Approximate quantity' => $fields['quantity'],
        'Packing brief' => fallback($fields['packaging'], 'Please advise'),
        'Target shipment window' => fallback($fields['timeline']),
        $site['notes_label'] => fallback($fields['message'], 'None supplied'),
        'Source page' => fallback($fields['source_page']),
        'Reference' => $leadId,
    ];

    $html = '<table role="presentation" style="width:100%;border-collapse:collapse;margin-top:20px">';
    foreach ($rows as $label => $value) {
        $html .= '<tr><th align="left" valign="top" style="width:38%;padding:10px;border-bottom:1px solid #dce6df;color:#244437;font-size:14px">' .
            escapeHtml($label) .
            '</th><td valign="top" style="padding:10px;border-bottom:1px solid #dce6df;color:#27342f;font-size:14px;white-space:pre-wrap">' .
            escapeHtml($value) .
            '</td></tr>';
    }
    return $html . '</table>';
}

/**
 * @param array<string, string> $site
 */
function emailShell(string $heading, string $content, array $site): string
{
    return '<!doctype html><html><body style="margin:0;background:#f4f0e6;font-family:Arial,sans-serif;color:#27342f">' .
        '<div style="max-width:680px;margin:0 auto;padding:28px 14px">' .
        '<div style="background:#123e31;color:#fff;padding:24px 28px;border-radius:14px 14px 0 0">' .
        '<p style="margin:0 0 6px;color:#f0ca74;font-size:13px;letter-spacing:.08em;text-transform:uppercase">UrbanFresh Rice Mills</p>' .
        '<h1 style="margin:0;font-size:26px;line-height:1.25">' . escapeHtml($heading) . '</h1></div>' .
        '<div style="background:#fff;padding:28px;border:1px solid #dce6df;border-top:0;border-radius:0 0 14px 14px;line-height:1.6">' .
        $content .
        '<p style="margin:28px 0 0;color:#65736d;font-size:13px">UrbanFresh Rice Mills · Karnal, Haryana, India<br>' .
        escapeHtml($site['desk_label']) . ': +91 94335 69217</p>' .
        '</div></div></body></html>';
}

/**
 * @param array<string, string> $fields
 * @param array<string, string> $site
 */
function ownerPlainText(array $fields, string $leadId, array $site): string
{
    return $site['owner_heading'] . "\n\n" . plainDetails($fields, $leadId, $site) .
        "\nReply directly to this message to contact the buyer.";
}

/**
 * @param array<string, string> $fields
 * @param array<string, string> $site
 */
function buyerPlainText(array $fields, string $leadId, array $site): string
{
    return "Hello {$fields['name']},\n\n" .
        $site['buyer_intro'] . "\n\n" .
        "This confirmation records your request; commercial feasibility, specification acceptance and terms remain subject to written review.\n\n" .
        plainDetails($fields, $leadId, $site) .
        "\nTo add documents, reply to this email or WhatsApp +91 94335 69217.";
}

/**
 * @param array<string, string> $fields
 * @param array<string, string> $site
 */
function plainDetails(array $fields, string $leadId, array $site): string
{
    return implode("\n", [
        'Name or company: ' . $fields['name'],
        'Phone / WhatsApp: ' . $fields['phone'],
        'Business email: ' . $fields['email'],
        $site['location_label'] . ': ' . $fields['location'],
        'Buyer type: ' . fallback($fields['buyer_type']),
        'Rice variety: ' . fallback($fields['variety'], 'Please advise'),
        'Processing: ' . fallback($fields['processing'], 'Please advise'),
        'Approximate quantity: ' . $fields['quantity'],
        'Packing brief: ' . fallback($fields['packaging'], 'Please advise'),
        'Target shipment window: ' . fallback($fields['timeline']),
        $site['notes_label'] . ': ' . fallback($fields['message'], 'None supplied'),
        'Reference: ' . $leadId,
    ]) . "\n";
}

function fallback(string $value, string $fallback = 'Not specified'): string
{
    return $value !== '' ? $value : $fallback;
}

function escapeHtml(string $value): string
{
    return htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

function subjectText(string $value): string
{
    return trim(str_replace(["\r", "\n"], ' ', $value));
}

/**
 * @param array<string, mixed> $payload
 */
function respond(int $status, array $payload): void
{
    http_response_code($status);
    if ($status !== 204) {
        echo json_encode($payload, JSON_UNESCAPED_SLASHES);
    }
    exit;
}
