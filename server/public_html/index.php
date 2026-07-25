<?php

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
header('X-Content-Type-Options: nosniff');

echo json_encode([
    'service' => 'UrbanFresh RFQ mailer',
    'status' => 'ready',
]);
