# AA Virtual Group - Static Website

> *A static website for Our Fellow Travelers, an online Alcoholics Anonymous group*

A simple, modern static website built with Next.js and React for Our Fellow Travelers virtual AA group. The site provides meeting information, calendar, downloads, and donation options.

## Features

- **Meeting Information**: Daily meeting details and access information
- **Google Calendar Integration**: Embedded calendar for group events
- **Downloads**: Links to A.A. literature and meeting materials
- **7th Tradition Donations**: Venmo and PayPal donation links
- **Responsive Design**: Mobile-friendly interface with dark mode support
- **Static Site**: Fast, secure, and easy to deploy

## Tech Stack

- **Next.js 15+** with App Router
- **React 19** with TypeScript
- **Tailwind CSS** for styling
- **shadcn/ui** components
- **Static Site Generation** for optimal performance

## Quick Start

### Prerequisites

- Node.js 18+ and npm
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/smcnary/awakenings-virtual-aa-group.git
   cd awakenings-virtual-aa-group
   ```

2. **Install dependencies**
   ```bash
   npm run setup
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```

4. **Access the application**
   - Open http://localhost:3000 in your browser

### Building for Production

```bash
npm run build
npm run start
```

## Configuration

### Google Calendar Embed

To add your Google Calendar:

1. Go to [Google Calendar](https://calendar.google.com)
2. Click the settings gear icon → Settings
3. Click on "Integrate calendar" in the left sidebar
4. Copy your Calendar ID (it looks like: `your-email@gmail.com` or a long string)
5. Open `frontend/src/app/calendar/page.tsx`
6. Replace `YOUR_CALENDAR_ID` in the iframe src URL with your actual Calendar ID

The calendar embed URL format:
```
https://calendar.google.com/calendar/embed?src=YOUR_CALENDAR_ID&ctz=America%2FChicago
```

### Donation Links

To configure Venmo and PayPal donation links:

1. **Venmo**: 
   - Get your Venmo username or QR code link
   - Update the Venmo link in:
     - `frontend/src/app/page.tsx` (home page)
     - `frontend/src/app/7th-tradition/page.tsx` (7th Tradition page)
   - Replace `https://venmo.com/your-username` with your actual Venmo link

2. **PayPal**:
   - Create a PayPal donation link at [PayPal.me](https://www.paypal.com/paypalme) or use PayPal Donate button
   - Update the PayPal link in:
     - `frontend/src/app/page.tsx` (home page)
     - `frontend/src/app/7th-tradition/page.tsx` (7th Tradition page)
   - Replace `https://www.paypal.com/donate/your-donation-link` with your actual PayPal link

## Project Structure

```
aa-virtual/
├── frontend/                 # Next.js application
│   ├── src/
│   │   ├── app/             # App Router pages
│   │   │   ├── page.tsx     # Home page
│   │   │   ├── calendar/    # Calendar page with Google Calendar embed
│   │   │   ├── downloads/   # Downloads page
│   │   │   └── 7th-tradition/ # 7th Tradition page
│   │   ├── components/      # Reusable UI components
│   │   │   ├── Navigation.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── ThemeProvider.tsx
│   │   │   └── ui/          # shadcn/ui components
│   │   └── lib/            # Utility functions
│   ├── public/             # Static assets
│   ├── package.json
│   └── next.config.ts
├── package.json            # Root package.json
└── README.md
```

## Deployment

### Vercel (Recommended)

1. Push your code to GitHub
2. Import your repository in [Vercel](https://vercel.com)
3. Configure build settings:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
4. Deploy

Vercel will automatically deploy on every push to your main branch.

### Netlify

1. Push your code to GitHub
2. Import your repository in [Netlify](https://netlify.com)
3. Configure build settings:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/.next`
4. Deploy

### Static Export (Alternative)

For a fully static site without Next.js server features:

1. Update `frontend/next.config.ts`:
   ```typescript
   const nextConfig: NextConfig = {
     output: 'export',
     // ... other config
   };
   ```

2. Build:
   ```bash
   cd frontend
   npm run build
   ```

3. Deploy the `frontend/out` directory to any static hosting service

## Development Commands

```bash
# Install all dependencies
npm run setup

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm run start
```

## Meeting Information

- **Time**: Daily at 7:00 a.m. Central Time
- **Platform**: FreeConferenceCall.com
- **Online Link**: https://join.freeconferencecall.com/timhwalton
- **Phone**: (951) 799-9267
- **Meeting ID**: timhwalton

## Contact

- **Email**: awakeningnstulsa@gmail.com
- **Facebook**: Private group (request to join)

## License & Disclaimer

This project is for educational and service purposes. All A.A. literature and materials are copyrighted by Alcoholics Anonymous World Services, Inc.

**This is not an official Alcoholics Anonymous website.** For official A.A. information, please visit [aa.org](https://www.aa.org/).

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

---

*"Our primary purpose is to stay sober and to help others recover from alcoholism."*

**The Twelve Steps, Twelve Traditions, and all other A.A. literature are copyrighted by A.A. World Services, Inc.**
