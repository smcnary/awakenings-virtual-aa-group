import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  webpack: (config, { dir, isServer }) => {
    // Get absolute path to src directory
    const srcPath = path.resolve(dir, "src");
    
    // Ensure resolve configuration exists
    config.resolve = config.resolve || {};
    config.resolve.alias = config.resolve.alias || {};
    
    // Set the @ alias to point to src directory
    // This allows imports like @/lib/utils to resolve to src/lib/utils
    config.resolve.alias["@"] = srcPath;
    
    // Preserve existing aliases
    const existingAliases = { ...config.resolve.alias };
    config.resolve.alias = {
      ...existingAliases,
      "@": srcPath,
    };
    
    return config;
  },
};

export default nextConfig;
