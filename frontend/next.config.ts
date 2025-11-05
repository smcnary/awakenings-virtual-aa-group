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
    // Use absolute path resolution - dir is already the project root (frontend/)
    const srcPath = path.resolve(dir, "src");
    
    config.resolve = config.resolve || {};
    config.resolve.alias = {
      ...(config.resolve.alias || {}),
      "@": srcPath,
    };
    
    return config;
  },
};

export default nextConfig;
