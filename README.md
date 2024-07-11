# Offer Generator
- This module takes in a current offer, generates more compelling offers, then evaluates
those compelling offers against Alex Hormozi's Value Framework.


# Src Folder
## offer_prompts
You will find the prompts in the prompts folder.

## models
You will find the LightRag Dataclasses.

## utils
CustomGenerator and CustomModelClient implementations.

## nuxt-app
You'll find the Nuxt front end application here.

# Getting Started
1. python -m venv venv
2. source venv/bin/activate
3. pip install -r requirements.txt
4. touch .env
    - ANTHROPIC_API_KEY=yourkey
5. fastapi dev app.py
6. Open another terminal
7. cd nuxt-app
8. npm install
9. npm run dev