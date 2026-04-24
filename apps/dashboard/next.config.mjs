// apps/dashboard/next.config.mjs
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  transpilePackages: ["@aegis/ui-web"],
  experimental: {
    typedRoutes: false,
  },
};

export default nextConfig;