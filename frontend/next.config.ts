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
    const srcPath = path.join(dir, "src");
    
    // Ensure alias is set correctly
    if (!config.resolve) {
      config.resolve = {};
    }
    if (!config.resolve.alias) {
      config.resolve.alias = {};
    }
    
    config.resolve.alias = {
      ...config.resolve.alias,
      "@": srcPath,
    };
    
    // Ensure modules array includes node_modules
    if (!config.resolve.modules) {
      config.resolve.modules = ["node_modules"];
    }
    
    return config;
  },
};

export default nextConfig;
