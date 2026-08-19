'use client'

import HeroSectionLanding from "@/components/HeroSectionLanding";
import TrustStrip from "@/components/TrustStrip";
import HowItWorks from "@/components/HowItWorks";
import FeatureSection from "@/components/FeatureSection";
import CTASection from "@/components/CTASection";

/*
|--------------------------------------------------------------------------
| Landing Page
|--------------------------------------------------------------------------
| This file only assembles all the sections.
| Every section lives inside its own component making the page modular.
|--------------------------------------------------------------------------
        ----------------------------------------------------------
        | Navbar                                                   |
        |----------------------------------------------------------|
        |                      HERO SECTION                        |
        |  Headline              Floating Glass Login Card         |
        |  Description                                             |
        |  CTA Buttons                                             |
        |----------------------------------------------------------|
        |               TRUST / FEATURE STRIP                      |
        |----------------------------------------------------------|
        |             HOW VOXFORM WORKS (3 Steps)                  |
        |----------------------------------------------------------|
        |          FEATURE CARDS (Glassmorphism)                   |
        |----------------------------------------------------------|
        |                      FOOTER                              |
         ----------------------------------------------------------
*/

export default function LandingPage() {
  
  return (
    <div className="min-h-screen text-white overflow-x-hidden">

      <main className="relative z-10">
        <HeroSectionLanding />
        <TrustStrip />
        <HowItWorks />
        <FeatureSection />
        <CTASection />
      </main>

    </div>
  );
}
