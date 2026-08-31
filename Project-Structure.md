🎙️ VoxForm AI
==============================

An AI based form filling application that uses voice based input to fill forms. It uses OpenAI Whisper and GPT to provide a quick and easy form filling interface. It provides an easy to navigate, pick-and-drop form builder interface powered by SurveyJS. Features a form management panel and provides a JWT-secured access with hierarchial role based access to teams and members.

#### Project Organization
------------

    ├── LICENSE
    ├── README.md               <- The top-level README for developers using this project.
    ├── app                     <- Backend source code
    │   ├─── main.py               - starting FastAPI service and app startup and config
    │   ├─── analytics             - Segregated based on services
    │   ├─── auth                  - Each service have their own separate router code
    │   ├─── core                  - Each service has its own response models, respository code
    │   ├─── forms                 - and related ORM models
    │   ├─── form_templates
    │   ├─── responses
    │   └─── voice
    |
    ├── frontend-next           <- Next.JS frontend directory
    │   ├─── api                   - all service wise API code and axios config code
    │   ├─── app                   - all app pages and layout code
    │   ├─── components            - all react components code used across pages
    │   ├─── public                - contains app logo
    │   ├─── .gitignore
    │   ├─── eslint.config.mjs     - To run frontend Next.JS app directly run:
    │   ├─── jsconfig.json              1. `npm install` - to get all necessary packages
    │   ├─── next.config.mjs            2. `npm run dev` - to start local dev server; hosting frontend app
    │   ├─── package-lock.json     - NOTE: start a backend FastAPI service separately for support.
    │   ├─── package.json
    │   └─── postcss.config.mjs
    |
    ├── frontend                <- Next.JS exported static frontend files
    │   └── out                    - All static files - HTML-JS
    |                              - exported using `npm run build` command 
    |
    ├── scripts                 <- python script to create user using terminal
    │   └── seed_org.py            - not useful; public sign-up available
    |
    ├── tests                   <- All test files
    |
    ├── .env.example            <- File to load app environment variables on docker run
    ├── requirements.txt        <- Requirements file for reproducing environment; for Docker use
    ├── .gitattributes
    └── .gitignore
   

--------
