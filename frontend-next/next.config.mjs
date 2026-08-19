/** @type {import('next').NextConfig} */
const nextConfig = {
    output: 'export', // Enables static HTML export
    images: {
        unoptimized: true, // Required for static exports if using next/image
    },
    trailingSlash: true,

    // COMMENT OUT - Cause 'rewrites' don't work with static files 'output'
    //               For connecting to FastAPI backend for APIs, we have changed the Axios code itself
    // async rewrites() {
    //     return [
    //     {
    //         source: '/api/:path*',
    //         destination: 'http://localhost:8000/api/:path*', // Your backend server
    //     },
    //     ];
    // },
};

export default nextConfig;
