Adding Tailwindcss

npx nuxi@latest module add tailwindcss


Install DaisyUI

npm i -D daisyui@latest

Update tailwind.config.js

module.exports = {
  //...
  plugins: [
    require('daisyui'),
  ],
}


