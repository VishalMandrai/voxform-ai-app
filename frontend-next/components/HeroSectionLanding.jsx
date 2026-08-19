'use client'

import HeroContent from "@/components/HeroContent";
import LoginCard from "@/components/LoginCard";

/*
|--------------------------------------------------------------------------
| Hero Section
|--------------------------------------------------------------------------
*/

export default function HeroSection() {

  return (
    <section id="hero-section" className="mt-10 mb-10 grid max-w-7xl items-center gap-20 px-6 
                lg:grid-cols-2">
      <HeroContent />
      <LoginCard />
    </section>
  );
}