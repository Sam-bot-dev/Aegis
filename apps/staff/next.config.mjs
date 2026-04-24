/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  transpilePackages: ["@aegis/ui-web"],
  experimental: {
    typedRoutes: false,
  },

  output: "export",
};

export default nextConfig;