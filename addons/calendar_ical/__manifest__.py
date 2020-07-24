{
    'name': "Calendar - iCal",
    'version': '0.0.85',
    'summary': 'Allow public and private download of user calendars as iCal.',

    'author': 'MetricWise, Inc.',
    'license': 'LGPL-3',
    'category': 'Tools',

    'depends': [
        'auth_basic',
        'auth_digest',
        'calendar',
    ],

    'external_dependencies': {
        'python': [
            'vobject',
        ],
    },
}
