<?php

return [
    'allowed_origins' => [
        'https://urbanfreshrice.com',
        'https://www.urbanfreshrice.com',
    ],
    'smtp' => [
        'host' => 'smtp.hostinger.com',
        'port' => 587,
        'encryption' => 'tls',
        'username' => 'noreply@urbanfreshrice.com',
        'password' => 'REPLACE_WITH_HOSTINGER_MAILBOX_PASSWORD',
    ],
    'from_email' => 'noreply@urbanfreshrice.com',
    'from_name' => 'UrbanFresh Rice Mills',
    'notification_email' => 'noreply@urbanfreshrice.com',
    'notification_name' => 'UrbanFresh International Buyer Desk',
    'rate_limit_per_hour' => 6,
];
