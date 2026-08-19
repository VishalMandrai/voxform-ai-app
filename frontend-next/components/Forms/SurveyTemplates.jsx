const SurveyTemplates = [
  { title: 'Gym Subscription Form', 
    description: 'All necessary details of new gym joiners and details of subscribed diet regimes and exercise plans.',
    total_questions: 11,
    created_on: '2nd August 2026',
    schema: [
            {
            "name": "page1",
            "title": "Basic Details",
            "elements": [
                {
                "type": "text",
                "name": "question1",
                "title": "First name:",
                "isRequired": true
                },
                {
                "type": "text",
                "name": "question2",
                "startWithNewLine": false,
                "title": "Last name:",
                "isRequired": true
                },
                {
                "type": "text",
                "name": "question3",
                "startWithNewLine": false,
                "title": "Phone Number",
                "isRequired": true,
                "inputType": "tel"
                },
                {
                "type": "text",
                "name": "question4",
                "title": "Date of Birth",
                "isRequired": true,
                "inputType": "date"
                },
                {
                "type": "text",
                "name": "question5",
                "startWithNewLine": false,
                "title": "Address",
                "isRequired": true
                }
            ]
            },
            {
            "name": "page2",
            "title": "Membership Details",
            "elements": [
                {
                "type": "radiogroup",
                "name": "question6",
                "title": "Membership Plan",
                "isRequired": true,
                "choices": [
                    {
                    "value": "Item 1",
                    "text": "Monthly - $40/month"
                    },
                    {
                    "value": "Item 2",
                    "text": "3-Monthly - $110"
                    },
                    {
                    "value": "Item 3",
                    "text": "6-Monthly - $210"
                    },
                    {
                    "value": "Item 4",
                    "text": "Annual - $360"
                    }
                ]
                },
                {
                "type": "checkbox",
                "name": "question7",
                "title": "Fitness Goals (Optional)",
                "choices": [
                    {
                    "value": "Item 1",
                    "text": "General Fitness"
                    },
                    {
                    "value": "Item 2",
                    "text": "Weight Loss"
                    },
                    {
                    "value": "Item 3",
                    "text": "Cardio / Endurance"
                    },
                    {
                    "value": "Item 4",
                    "text": "Flexibility / Mobility"
                    }
                ],
                "showOtherItem": true,
                "otherText": "Other"
                },
                {
                "type": "checkbox",
                "name": "question8",
                "startWithNewLine": false,
                "title": "Add-on Services",
                "choices": [
                    {
                    "value": "Item 1",
                    "text": "Personal Training - $25 / session"
                    },
                    {
                    "value": "Item 2",
                    "text": "Group Classes - $15 / month"
                    },
                    {
                    "value": "Item 3",
                    "text": "Nutrition Guidance - $30 / month"
                    },
                    {
                    "value": "Item 4",
                    "text": "Locker Rental -$10 / month"
                    },
                    {
                    "value": "Item 5",
                    "text": "Towel Service - $20 / month"
                    }
                ],
                "showNoneItem": true,
                "showSelectAllItem": true
                }
            ]
            },
            {
            "name": "page3",
            "title": "Payment Details",
            "elements": [
                {
                "type": "dropdown",
                "name": "question9",
                "title": "Payment Method",
                "isRequired": true,
                "choices": [
                    {
                    "value": "Item 1",
                    "text": "Credit Card"
                    },
                    {
                    "value": "Item 2",
                    "text": "Debit Card"
                    },
                    {
                    "value": "Item 3",
                    "text": "UPI"
                    },
                    {
                    "value": "Item 4",
                    "text": "Bank Transfer"
                    },
                    {
                    "value": "Item 5",
                    "text": "Cash"
                    }
                ]
                },
                {
                "type": "dropdown",
                "name": "question10",
                "startWithNewLine": false,
                "title": "Billing Frequency",
                "isRequired": true,
                "choices": [
                    {
                    "value": "Item 1",
                    "text": "Monthly"
                    },
                    {
                    "value": "Item 2",
                    "text": "Quaterly"
                    },
                    {
                    "value": "Item 3",
                    "text": "One Time Full Pay"
                    }
                ]
                },
                {
                "type": "text",
                "name": "question11",
                "startWithNewLine": false,
                "title": "Start Date",
                "isRequired": true,
                "inputType": "date"
                }
            ]
            }
        ],
  },
  { title:  "Insurance Cancellation Form", 
    description:  "Form to cancel Insurance Policy at LIC.",
    total_questions: 15,
    created_on: '3rd August 2026',
    schema:  [
                {
                "name": "page1",
                "title": "Basic Details",
                "elements": [
                    {
                    "type": "text",
                    "name": "question1",
                    "title": "First name:",
                    "isRequired": true
                    },
                    {
                    "type": "text",
                    "name": "question2",
                    "startWithNewLine": false,
                    "title": "Last name:",
                    "isRequired": true
                    },
                    {
                    "type": "text",
                    "name": "question3",
                    "startWithNewLine": false,
                    "title": "Phone Number",
                    "isRequired": true,
                    "inputType": "tel"
                    },
                    {
                    "type": "text",
                    "name": "question4",
                    "title": "Date of Birth",
                    "isRequired": true,
                    "inputType": "date"
                    },
                    {
                    "type": "text",
                    "name": "question6",
                    "startWithNewLine": false,
                    "title": "Email",
                    "inputType": "email"
                    },
                    {
                    "type": "text",
                    "name": "question5",
                    "title": "Home Address",
                    "isRequired": true
                    }
                ]
                },
                {
                "name": "page2",
                "title": "Insurance Policy Details",
                "elements": [
                    {
                    "type": "text",
                    "name": "question7",
                    "title": "Insurance Agent Name",
                    "isRequired": true
                    },
                    {
                    "type": "text",
                    "name": "question8",
                    "title": "Policy Number",
                    "isRequired": true,
                    "inputType": "number"
                    },
                    {
                    "type": "text",
                    "name": "question9",
                    "startWithNewLine": false,
                    "title": "Effective Date of Cancellation",
                    "isRequired": true,
                    "inputType": "date"
                    },
                    {
                    "type": "radiogroup",
                    "name": "question10",
                    "title": "Type of Insurance",
                    "isRequired": true,
                    "choices": [
                        {
                        "value": "Item 1",
                        "text": "Health"
                        },
                        {
                        "value": "Item 2",
                        "text": "Life"
                        },
                        {
                        "value": "Item 3",
                        "text": "Automotive"
                        },
                        {
                        "value": "Item 4",
                        "text": "Home"
                        }
                    ],
                    "showOtherItem": true
                    }
                ]
                },
                {
                "name": "page3",
                "title": "Cancellation and Refund",
                "elements": [
                    {
                    "type": "text",
                    "name": "question12",
                    "title": "Bank Name",
                    "isRequired": true
                    },
                    {
                    "type": "text",
                    "name": "question13",
                    "startWithNewLine": false,
                    "title": "Account Number",
                    "isRequired": true,
                    "inputType": "number"
                    },
                    {
                    "type": "text",
                    "name": "question14",
                    "startWithNewLine": false,
                    "title": "Routing Number",
                    "isRequired": true,
                    "inputType": "number"
                    },
                    {
                    "type": "dropdown",
                    "name": "question11",
                    "title": "Reason for Cancellation",
                    "choices": [
                        {
                        "value": "Item 1",
                        "text": "Switching to another provider"
                        },
                        {
                        "value": "Item 2",
                        "text": "No longer need coverage"
                        },
                        {
                        "value": "Item 3",
                        "text": "Found a better rate"
                        }
                    ],
                    "showOtherItem": true
                    }
                ]
                },
                {
                "name": "page4",
                "title": "Final Consent",
                "elements": [
                    {
                    "type": "checkbox",
                    "name": "question15",
                    "isRequired": true,
                    "choices": [
                        {
                        "value": "Item 1",
                        "text": "Please cancel my insurance policy as of the specified date. Refunds will be processed as per policy terms."
                        }
                    ]
                    }
                ]
                }
            ],
  },
//   { title:  "Insurance Cancellation Form", 
//     description:  "Form to cancel Insurance Policy at LIC.",
//     total_questions: 15,
//     created_on: '3rd August 2026',
//     schema: [],
//   },
]

export default SurveyTemplates
