# Qwen Agent Frontend

This directory contains the frontend interface for the Qwen Agent application, built with Webpack for modern development workflow.

## Structure

```
frontend/
├── src/                    # Source files
│   ├── index.html          # HTML template
│   ├── index.js            # Main entry point
│   ├── css/
│   │   └── styles.css      # All styling with CSS custom properties
│   ├── js/
│   │   ├── config.js       # Configuration object
│   │   └── chat.js         # Chat functionality
│   └── assets/             # Static assets (images, icons, etc.)
├── dist/                   # Built files (generated)
├── webpack.config.js       # Webpack configuration
├── package.json            # Dependencies and scripts
└── README.md               # This file
```

## Features

- **Modern Build System**: Webpack with hot reloading and optimization
- **Real-time Chat Interface**: Uses Server-Sent Events (SSE) for live streaming responses
- **Markdown Support**: Assistant responses are rendered with markdown formatting
- **Thinking Indicators**: Shows the AI's thinking process in real-time
- **Responsive Design**: Works on desktop and mobile devices
- **Error Handling**: Graceful error handling and status indicators
- **CSS Custom Properties**: Easy theming and customization

## Development

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn

### Setup

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Start development server**:
   ```bash
   npm run dev
   ```
   
   This will:
   - Start the development server on `http://localhost:3000`
   - Enable hot reloading
   - Open the browser automatically

### Available Scripts

- `npm run dev` or `npm start` - Start development server with hot reloading
- `npm run build` - Build for production (optimized)
- `npm run build:dev` - Build for development (with source maps)

## Production

### Building for Production

```bash
npm run build
```

This creates optimized files in the `dist/` directory:
- Minified JavaScript with content hashing
- Extracted and minified CSS
- Optimized assets
- HTML with proper asset references

### Serving Production Build

The `dist/` directory contains all the files needed to serve the application. You can serve it with any static file server:

```bash
# Using Python
python -m http.server 8080

# Using Node.js
npx serve dist

# Using nginx, Apache, or any web server
```

## Configuration

### API Configuration

Edit `src/js/config.js` to customize:
- API URL and endpoints
- UI settings
- Messages and status text
- Animation timing

### Styling

Edit `src/css/styles.css` - modify the CSS custom properties in the `:root` section:
```css
:root {
    --primary-color: #your-color;
    --background-color: #your-bg-color;
    /* ... other variables */
}
```

## Webpack Features

- **Hot Module Replacement**: Instant updates during development
- **Code Splitting**: Automatic vendor chunk separation
- **Asset Optimization**: Image and font optimization
- **Source Maps**: Debugging support in development
- **CSS Extraction**: Separate CSS files in production
- **Clean Builds**: Automatic cleanup of old builds

## Browser Compatibility

- Modern browsers with ES6+ support
- Requires EventSource API for SSE functionality
- Marked.js library for markdown parsing

## Troubleshooting

1. **Port conflicts**: If port 3000 is in use, Webpack will automatically try the next available port
2. **CORS Issues**: Ensure the backend has proper CORS configuration for `http://localhost:3000`
3. **Build errors**: Check that all imports are correct and dependencies are installed
4. **Hot reload not working**: Try refreshing the browser or restarting the dev server

## Development Workflow

1. **Start backend server** (make sure it's running on `http://localhost:8002`)
2. **Run `npm run dev`** to start the frontend development server
3. **Edit files in `src/`** - changes will automatically reload
4. **Build for production** with `npm run build` when ready to deploy 