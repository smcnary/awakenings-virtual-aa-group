import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  webpack: (config, { dir }) => {
    // Get absolute path to src directory
    const srcPath = path.resolve(dir, "src");
    
    // Ensure resolve configuration exists
    config.resolve = config.resolve || {};
    config.resolve.alias = config.resolve.alias || {};
    
    // Set the @ alias to point to src directory
    // This allows imports like @/lib/utils to resolve to src/lib/utils
    // Important: Use path.resolve to ensure absolute path
    config.resolve.alias = {
      ...config.resolve.alias,
      "@": srcPath,
    };
    
    // Debug: Log the alias configuration (only in development)
    if (process.env.NODE_ENV === "development") {
      console.log("Webpack alias @ configured to:", srcPath);
    }
    
    return config;
  },
};

export default nextConfig;
