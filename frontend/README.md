# DataFlow AI - Premium Analytics Dashboard v2.0

Professional Tailwind CSS frontend for the Data Analyst Agent with modern UI/UX and smooth animations.

## ✨ Features

### 🎨 Design & Styling
- **Premium Dark Theme** with professional color palette
- **Tailwind CSS** - Utility-first CSS framework for rapid development
- **Glassmorphism Effects** - Modern frosted glass UI components
- **Gradient Accents** - Beautiful gradient text and backgrounds
- **Smooth Animations** - 12+ custom animations (fade-in, slide, spin, float, glow)
- **Responsive Design** - Works seamlessly on mobile, tablet, and desktop
- **CSS Variables** - Easy theming and customization

### 💬 Chat Interface
- Real-time message display with user/bot distinction
- Syntax highlighting for code blocks (Highlight.js integration)
- Markdown support (bold, italic, code, links)
- Auto-scrolling to latest messages
- Message history persistence

### 📊 Data Management
- **Drag-drop file upload** for CSV, XLSX, JSON files
- File size validation (50MB limit)
- File metadata tracking
- Upload progress indicators
- Multiple file support

### 🔌 Backend Integration
- Auto health checks every 30 seconds
- Auto-reconnect logic on connection loss
- Graceful error handling
- Status indicator showing connection state
- Support for three API endpoints

### 📈 Quick Actions
- Summary generation
- Statistics calculation
- Visualization suggestions
- Key insights extraction
- Template-based queries

### 📱 Responsive Breakpoints
- **Desktop** (1024px+): Full sidebar layout with right panel
- **Tablet** (768px+): Sidebar visible, compact layout
- **Mobile** (< 768px): Hamburger menu, optimized for touch

### 💾 Data Persistence
- LocalStorage for conversation history
- Recent queries tracking (last 10)
- File metadata storage
- Auto-save after each message

### 🔒 Security
- HTML escaping for XSS protection
- File type and size validation
- Input sanitization
- HTTPS ready for production

## 🚀 Quick Start

### Installation
```bash
cd frontend
npm install
```

### Development
```bash
npm run dev
```
Opens at `http://localhost:3000` with live CSS rebuilding

### Production Build
```bash
npm run build:prod
npm start
```

### Deploy to Railway
```bash
git add .
git commit -m "Deploy Tailwind v2.0"
git push
```

## 📁 Project Structure

```
frontend/
├── index.html              # Main HTML structure
├── app.js                  # JavaScript logic
├── styles/
│   ├── input.css          # Tailwind directives
│   └── output.css         # Compiled CSS
├── tailwind.config.ts     # Tailwind config
└── package.json           # Dependencies
```

## 🎨 Colors & Theme

All colors use CSS variables for easy customization:

- **Primary**: Blue (`#3b82f6`)
- **Accent**: Violet (`#8b5cf6`)
- **Secondary**: Indigo (`#6366f1`)
- **Background**: Deep slate (`#0f172a`)
- **Card**: Slate (`#1e293b`)

Edit `styles/input.css` to customize colors.

## 🎬 Animations

Smooth, professional animations powered by Tailwind:

- `fade-in` - 0.6s entrance
- `slide-in-left` - 0.6s sidebar
- `slide-in-right` - 0.6s toast
- `scale-in` - 0.3s modals
- `spin-slow` - 6s loading
- `float` - 3s icons
- `glow` - 2s emphasis
- `pulse` - Status dots

## 🔗 Backend Integration

**URL**: `https://web-production-0249c.up.railway.app`

### Endpoints
- `GET /health` - Health check
- `POST /api/analyze` - Send query
- `POST /api/upload` - Upload file

## 🛠️ Customization

### Change Colors
Edit `styles/input.css`:
```css
:root {
  --primary: 222.2 47.6% 11.2%;
  --accent: 217.2 91.2% 59.8%;
}
```

### Change Backend URL
Edit `app.js` line 8:
```javascript
const API_URL = 'https://your-url.com';
```

## 📦 Dependencies

- `tailwindcss` - CSS framework
- `serve` - Static server
- `postcss` - CSS processing
- `autoprefixer` - Vendor prefixes

## 🌐 Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- iOS Safari 14+
- Android browsers

## ⚡ Performance

- Load Time: < 2 seconds
- CSS Size: ~50KB minified
- JS Size: ~18KB
- Total: ~70KB

## 🚨 Troubleshooting

**Styles not loading**
```bash
npm run build:prod
# Clear cache: Ctrl+Shift+Delete
```

**Backend not connecting**
- Check URL in `app.js`
- Verify backend is running
- Check CORS configuration

**File upload fails**
- Verify file type (CSV, XLSX, JSON)
- Check file size (< 50MB)
- Ensure backend endpoint works

## 🎯 Features Roadmap

- [ ] Light/Dark theme switcher
- [ ] Component library
- [ ] Advanced charts
- [ ] Export to PDF/CSV
- [ ] Real-time collaboration
- [ ] Voice input

## 📝 License

MIT - See LICENSE file

---

**Version**: 2.0.0 | Built with Tailwind CSS, HTML, & Vanilla JS
