# Tailspin Toys — Frontend

This is the frontend for the Tailspin Toys crowdfunding platform, built with [Astro](https://astro.build/), [Svelte](https://svelte.dev/), and [Tailwind CSS](https://tailwindcss.com/).

## Project Structure

```text
client/
├── public/              # Static assets (favicon, etc.)
├── src/
│   ├── components/      # Reusable Svelte components
│   │   ├── GameList.svelte    # Renders the list of games on the home page
│   │   ├── GameDetails.svelte # Renders the details for a single game
│   │   └── Header.astro       # Site header / navigation
│   ├── layouts/         # Astro layout templates
│   ├── pages/           # Astro page routes
│   │   ├── index.astro        # Home page — games listing
│   │   ├── about.astro        # About page
│   │   └── game/
│   │       └── [id].astro     # Dynamic game detail page
│   └── styles/          # Global CSS and Tailwind configuration
├── e2e-tests/           # Playwright end-to-end tests
├── astro.config.mjs
├── svelte.config.js
├── tailwind.config.*
└── package.json
```

## Commands

All commands are run from the `client/` directory:

| Command              | Action                                      |
| :------------------- | :------------------------------------------ |
| `npm install`        | Install dependencies                        |
| `npm run dev`        | Start local dev server at `localhost:4321`  |
| `npm run build`      | Build the production site to `./dist/`      |
| `npm run preview`    | Preview the production build locally        |
| `npm run test:e2e`   | Run Playwright end-to-end tests             |

> **Tip:** To start both the frontend and the Flask backend together, run `../scripts/start-app.sh` from the project root.

## End-to-End Tests

Playwright tests live in `e2e-tests/`. Run them with:

```bash
npm run test:e2e
```

Make sure the application is running (both backend and frontend) before executing tests.
