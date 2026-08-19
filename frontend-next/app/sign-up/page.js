'use client'

import HeroSectionSignup from "@/components/HeroSectionSignup";
import TrustStrip from "@/components/TrustStrip";
import HowItWorks from "@/components/HowItWorks";
import FeatureSection from "@/components/FeatureSection";
import CTASection from "@/components/CTASection";

import { useRouter } from "next/navigation";

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

export default function SignUp() {
  const navigation = useRouter()
  
  return (
    <div className="min-h-screen text-white overflow-x-hidden">

      <main className="relative z-10">
        <HeroSectionSignup />
        <TrustStrip />
        <HowItWorks />
        <FeatureSection />
        <CTASection />
      </main>

    </div>
  );
}

