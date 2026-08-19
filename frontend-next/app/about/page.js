"use client";   

/**
 * AboutPage.jsx — Comprehensive About page for VoxForm AI
 *
 * A visually rich, fully self-contained page built with Tailwind CSS utility
 * classes. It covers:
 *   - Hero section with product positioning
 *   - How It Works (3-step voice pipeline)
 *   - Core Feature Cards (voice input, form builder, auth, dashboard, etc.)
 *   - Technology Stack (frontend, backend, AI/ML, database)
 *   - Security Architecture
 *   - Role System (Org Admin vs Respondent)
 *   - Roadmap / Future Features
 *   - CTA footer strip
 *
 * Tailwind note: this file uses standard Tailwind utility classes only.
 * Ensure your project has Tailwind v3+ configured and the content path
 * for this file included in tailwind.config.js.
 */

import { useEffect, useState } from "react";
import Link from 'next/link';

import Footer from '@/components/Footer'
import Image from 'next/image';
import Logo from '@/public/voxform-logo.svg'


// ─────────────────────────────────────────────────────────────────────────────
// Small reusable primitives
// ─────────────────────────────────────────────────────────────────────────────

/** Gradient pill badge */
function Badge({ children, color = "blue" }) {
  const palettes = {
    blue:   "bg-blue-100 text-blue-700 border border-blue-200",
    violet: "bg-violet-100 text-violet-700 border border-violet-200",
    emerald:"bg-emerald-100 text-emerald-700 border border-emerald-200",
    amber:  "bg-amber-100 text-amber-700 border border-amber-200",
    rose:   "bg-rose-100 text-rose-700 border border-rose-200",
    slate:  "bg-slate-100 text-slate-600 border border-slate-200",
  };
  return (
    <span className={`inline-block text-xs font-semibold px-3 py-1 rounded-full ${palettes[color]}`}>
      {children}
    </span>
  );
}

/** Section heading with optional subtitle */
function SectionHeading({ eyebrow, title, subtitle, center = true }) {
  return (
    <div className={center ? "text-center max-w-8xl mx-auto mb-12" : "mb-10"}>
      {eyebrow && (
        <span className="text-8xl font-semibold tracking-widest text-sky-400 uppercase">
          {eyebrow}
        </span>
      )}
      <br></br>
      <br></br>
      <span className="text-4xl sm:text-4xl font-extrabold text-zinc-400 leading-tight mb-4">
        {title}
      </span>
      {subtitle && (
        <p className="text-xl text-white leading-relaxed">{subtitle}</p>
      )}
    </div>
  );
}

/** Glowing card wrapper */
function Card({ children, className = "" }) {
  return (
    <div
      className={`bg-white rounded-2xl border border-slate-200 shadow-sm hover:shadow-md
                  transition-shadow duration-300 p-6 ${className}`}
    >
      {children}
    </div>
  );
}

/** Icon circle with gradient background */
function IconCircle({ icon, gradient }) {
  return (
    <div
      className={`w-14 h-14 rounded-xl flex items-center justify-center text-white text-2xl mb-4 ${gradient}`}
    >
      {icon}
    </div>
  );
}

/** A single tech-stack pill with logo placeholder */
function TechPill({ name, category, icon, color }) {
  const colors = {
    blue:   "bg-blue-650 border-blue-200 text-blue-400",
    orange: "bg-orange-650 border-orange-200 text-orange-400",
    green:  "bg-green-650 border-green-200 text-green-400",
    purple: "bg-purple-650 border-purple-200 text-purple-400",
    yellow: "bg-yellow-650 border-yellow-200 text-yellow-400",
    slate:  "bg-slate-650 border-slate-200 text-slate-400",
    teal:   "bg-teal-650 border-teal-200 text-teal-400",
    red:    "bg-red-650 border-red-200 text-red-400",
  };
  return (
    <div className={`inline-flex items-center gap-2 border rounded-xl px-2 py-5 ${colors[color]}`}>
      <span className="text-2xl">{icon}</span>
      <div>
        <span className="font-semibold text-lg leading-none">{name}</span>
        <br></br>
        <span className="text-sm/1 opacity-70 mt-0.5">{category}</span>
      </div>
    </div>
  );
}

/** Animated step connector for the pipeline */
function StepConnector() {
  return (
    <div className="hidden md:flex items-center justify-center flex-1 px-2">
      <div className="flex items-center gap-1">
        {[0, 1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="w-1.5 h-1.5 rounded-full bg-blue-300"
            style={{ opacity: 0.4 + i * 0.15 }}
          />
        ))}
        <div className="w-0 h-0 border-l-8 border-l-blue-400 border-y-4 border-y-transparent ml-0.5" />
      </div>
    </div>
  );
}

/** Accordion row for FAQ-style sections */
function AccordionItem({ question, answer }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="border border-slate-200 rounded-xl overflow-hidden">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between px-5 py-4 bg-zinc-950 hover:bg-slate-50
                   hover:text-zinc-950 text-left font-semibold text-slate-100 transition-colors"
      >
        {question}
        <span
          className={`ml-4 text-sky-400 text-xl font-bold transition-transform 
                      duration-200 ${open ? "rotate-45" : ""}`}
        >
          ＋
        </span>
      </button>
      {open && (
        <div className="px-5 pb-5 pt-0 bg-white text-slate-600 text-xl leading-relaxed border-t border-slate-100">
          {answer}
        </div>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Section components
// ─────────────────────────────────────────────────────────────────────────────

/** ── 1. HERO ── */
function HeroSection() {
  return (
    <section className="relative overflow-hidden bg-gradient-to from-sky-900 via-zinc-950 
                        to-black-900 text-white">
      {/* Background grid */}
      <div
        className="absolute inset-0 opacity-10"
        style={{
          backgroundImage:
            "linear-gradient(to right, #1b2d4b 1px, transparent 1px), linear-gradient(to bottom, #1b2d4b 1px, transparent 1px)",
          backgroundSize: "48px 48px",
        }}
      />

      {/* Radial glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[500px] bg-blue-600 opacity-10 rounded-full blur-3xl pointer-events-none" />

      <div className="relative max-w-6xl mx-auto px-6 py-20 sm:py-32 text-center">
        
        {/* Logo mark */}
        <div className="inline-flex items-center gap-3 mb-3">
          {/* <Image 
            src={Logo} 
            alt="App logo" 
            width={250} // Set appropriate dimensions
            height={100}
          /> */}


          {/* <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-400 to-violet-500 
                              flex items-center justify-center shadow-lg shadow-blue-500/40">
            <span className="text-2xl">🎙️</span>
          </div> */}
          <span className="text-6xl font-black tracking-tight text-sky-400">
            Vox<span className="text-white">Form</span>
            <span className="ml-1.5 text-6xl font-semibold px-2 py-0 bg-blue-500/20 border 
                            border-blue-400/30 rounded-xl align-middle text-blue-300">
              AI
            </span>
          </span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold leading-tight mb-6 tracking-tight">
          Fill Surveys at the{" "}
          <span className="bg-gradient-to-r from-sky-500 to-sky-200 bg-clip-text text-transparent">
            Speed of Speech
          </span>
        </h1>

        <p className="max-w-2xl mx-auto text-lg sm:text-xl text-slate-300 leading-relaxed mb-8">
          VoxForm AI transforms how organisations collect data. <br></br>
          Speak naturally — our AI transcribes your voice, understands your intent, and fills every
          form field in real time. 
        </p>
        <span className="text-[28px] font-mono font-semibold">
          No more CLICKING. No more TYPING.
        </span>

        {/* Metric pills */}
        <div className="flex flex-wrap items-center justify-center gap-4 mb-10 mt-8">
          {[
            { icon: "⚡", label: "10× faster data collection" },
            { icon: "🎯", label: "LLM-powered field extraction" },
            { icon: "🔒", label: "JWT-secured multi-tenant auth" },
            // { icon: "📊", label: "Built-in analytics dashboard" },
          ].map((item) => (
            <div
              key={item.label}
              className="flex items-center gap-2 bg-zinc-800/10 backdrop-blur-sm border border-white/15
                         rounded-full px-4 py-2 text-xl font-medium text-slate-200"
            >
              <span>{item.icon}</span>
              {item.label}
            </div>
          ))}
        </div>

        {/* CTA buttons */}
        <div className="flex flex-wrap items-center justify-center gap-4 mt-4">
          <Link
            href="#how-it-works"
            className="px-7 py-3.5 bg-blue-500 hover:bg-blue-400 text-white font-semibold
                       rounded-xl transition-colors shadow-lg shadow-blue-500/30 text-l"
          >
            See How It Works →
          </Link>
          <Link
            href="#tech-stack"
            className="px-7 py-3.5 bg-white/10 hover:bg-white/20 border border-white/20
                       text-white font-semibold rounded-xl transition-colors text-l"
          >
            Tech Stack
          </Link>
        </div>
      </div>

      {/* Bottom fade */}
      <div className="absolute bottom-0 inset-x-0 h-16 bg-gradient-to-t from-black to-transparent" />
    </section>
  );
}

/** ── 2. STATS BAR ── */
function StatsBar() {
  const stats = [
    { value: "< 2s", label: "Avg. transcription time", icon: "⏱️" },
    { value: "3-step", label: "Voice → LLM Extract → Fill pipeline", icon: "🔄" },
    { value: "2-tier", label: "Role system (Admin + Respondent)", icon: "👥" },
    { value: "∞", label: "Form complexity via SurveyJS", icon: "📋" },
  ];

  return (
    <section className="bg-black">
      <div className="max-w-8xl mx-auto px-6 py-10 grid grid-cols-2 md:grid-cols-4 gap-6">
        {stats.map((s) => (
          <div key={s.label} className="text-center">
            <div className="text-3xl mb-1">{s.icon}</div>
            <div className="text-3xl sm:text-3xl font-mono font-bold text-sky-400 leading-none">
              {s.value}
            </div>
            <div className="text-xl text-slate-300 mt-1.5 leading-snug">{s.label}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

/** ── 3. HOW IT WORKS ── */
function HowItWorksSection() {
  const steps = [
    {
      number: "01",
      icon: "🎤",
      title: "Speak Naturally",
      desc: "The user opens a form and clicks the microphone button. They speak their answers in natural language — no special syntax, no commands. The browser's MediaRecorder API captures the audio stream in real time.",
      detail: "Supports WebM, WAV, and any browser-native audio format. Max 25 MB per recording.",
      gradient: "from-sky-400 to-sky-600",
    },
    {
      number: "02",
      icon: "🔊",
      title: "Whisper Transcribes",
      desc: "The audio clip is sent to the FastAPI backend and processed by OpenAI's Whisper model via the Groq API — one of the fastest inference providers available. Groq's LPU hardware delivers transcriptions in under 2 seconds on average.",
      detail: "Groq-hosted Whisper large-v3. Supports 50+ languages.",
      gradient: "from-sky-500 to-violet-500",
    },
    {
      number: "03",
      icon: "🧠",
      title: "LLM Extracts Fields",
      desc: "The transcript is passed to a Groq-hosted LLM (e.g. OpenAI GPT) alongside the form's field schema (labels, types, options). The model returns a structured JSON mapping each spoken answer to its correct field — including fuzzy-matching for choice fields.",
      detail: "Temperature 0 for deterministic extraction. Field IDs validated post-parse.",
      gradient: "from-emerald-500 to-emerald-800",
    },
    {
      number: "04",
      icon: "✍️",
      title: "Form Fills Dynamically",
      desc: "The React frontend receives the extracted values and immediately pre-populates every matched field.",
      // extra desc: A confidence score (0–100%) is shown next to each field so the respondent knows which answers to double-check before submitting.
      detail: "Unmatched fields stay blank for manual entry. Transcript shown for review.",
      gradient: "from-amber-500 to-amber-900",
    },
    {
      number: "05",
      icon: "✅",
      title: "Review & Submit",
      desc: "The user reviews the pre-filled fields, corrects any mistakes using standard inputs, and submits. The response is validated server-side (required fields, choice constraints, number format) before being persisted to MySQL.",
      // extra desc: and surfaced in the analytics dashboard
      detail: "Raw transcript stored alongside structured answers for audit trails.",
      gradient: "from-rose-500 to-rose-900",
    },
  ];

  return (
    <section id="how-it-works" className="bg-gradient-to from-sky-900 via-zinc-950 
                        to-black-900 py-24">
      <div className="max-w-7xl mx-auto px-6">
        <SectionHeading
          eyebrow="The pipeline"
          title="How VoxForm AI Works"
          subtitle="Five steps from microphone click to submitted form — all happening in under 5 seconds."
        />

        {/* Timeline grid */}
        <div className="relative">
          {/* Connecting line (desktop) */}
          <div className="hidden md:block absolute top-8 left-[calc(10%+1.5rem)] right-[calc(10%+1.5rem)] h-0.5 bg-gradient-to-r from-blue-900 via-violet-200 to-rose-900" />

          <div className="grid md:grid-cols-5 gap-6">
            {steps.map((step) => (
              <div key={step.number} className="flex flex-col items-center text-center group">
                {/* Circle */}
                <div
                  className={`relative z-10 w-20 h-20 rounded-2xl bg-gradient-to-br ${step.gradient}
                               flex items-center justify-center text-white text-4xl shadow-lg mb-4
                               group-hover:scale-110 transition-transform duration-200`}
                >
                  {step.icon}
                  <span className="absolute -top-4 -right-5 w-10 h-10 rounded-full bg-black border-2 border-slate-200 text-[14px] font-black text-zinc-300 flex items-center justify-center leading-none">
                    {step.number}
                  </span>
                </div>

                <span className="font-semibold text-slate-200 mb-2 text-xl sm:text-xl">
                  {step.title}
                </span>
                <span className="text-xl text-slate-500 leading-relaxed mb-2 min-h-110">
                  {step.desc}
                </span>
                <span className="min-h-40 font-mono text-m text-zinc-200 bg-zinc-950 border
                                 border-blue-100 rounded-lg px-2 py-5 leading-snug">
                  {step.detail}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

/** ── 4. CORE FEATURES ── */
function CoreFeaturesSection() {
  const features = [
    {
      icon: "🎙️",
      gradient: "from-blue-500 to-blue-600",
      title: "Real-time Voice Filling",
      badge: { label: "Core Feature", color: "blue" },
      body: "Respondents click one button, speak naturally, and watch every form field populate instantly. The browser MediaRecorder captures audio; the Groq-powered Whisper model transcribes it; the LLM maps answers to fields.",
      bullets: [
        "Multi-language transcription (50+ languages)",
        "Confidence scores highlight uncertain extractions",
        "Verbatim transcript stored for audit trails",
        "Manual correction of any pre-filled field",
      ],
    },
    {
      icon: "🏗️",
      gradient: "from-violet-500 to-violet-600",
      title: "Advanced Form Builder",
      badge: { label: "SurveyJS Powered", color: "violet" },
      body: "Org admins design forms of any complexity using a drag-and-drop interface powered by SurveyJS — the industry-leading open-source form framework. No coding required.",
      bullets: [
        "30+ question types: text, rating, matrix, image selector…",
        "Conditional logic and branching",
        "Multi-page forms with progress indicators",
        "Global template library — clone and customise",
      ],
    },
    {
      icon: "🔐",
      gradient: "from-emerald-500 to-emerald-600",
      title: "JWT Authentication",
      badge: { label: "Security First", color: "emerald" },
      body: "Every session is backed by a signed HS256 JWT stored in an HttpOnly cookie — inaccessible to JavaScript, immune to XSS. The token embeds user_id, org_id, and role so every API call is instantly verifiable without a DB round-trip.",
      bullets: [
        "HttpOnly + SameSite=Lax cookies — no localStorage",
        "7-day token expiry, configurable per deployment",
        "bcrypt password hashing (work factor 12)",
        "Org-scoped data isolation — multi-tenant by design",
      ],
    },
    {
      icon: "🏢",
      gradient: "from-amber-500 to-amber-600",
      title: "Organisation & Team Management",
      badge: { label: "Multi-tenant", color: "amber" },
      body: "Every deployment is org-scoped. Org Admins manage their team via a one-click invite system. Invites carry the recipient's name, email, and role — the invitee only needs to set a password.",
      bullets: [
        "Invite-only model — no public signup",
        "Invite link shown once; token valid 7 days",
        "Two roles: Org Admin & Respondent",
        "Seed script for the first org + admin",
      ],
    },
    // {
    //   icon: "📊",
    //   gradient: "from-rose-500 to-rose-600",
    //   title: "Analytics Dashboard",
    //   badge: { label: "Phase 3", color: "rose" },
    //   body: "Org Admins see a real-time analytics dashboard for every form: total responses, 30-day trend charts, per-field breakdowns (choice distributions, number stats), and completion rates.",
    //   bullets: [
    //     "Chart.js / react-chartjs-2 interactive charts",
    //     "Completion rate: % of responses with all required fields",
    //     "Horizontal bar charts for choice field distributions",
    //     "CSV export with one-click download",
    //   ],
    // },
    {
      icon: "📤",
      gradient: "from-teal-500 to-teal-600",
      title: "CSV Export",
      badge: { label: "Data Portability", color: "slate" },
      body: "Download all responses for a form as a clean, analysis-ready CSV in one click. Each response is a row; each form field is a column. Duplicate field labels are automatically disambiguated.",
      bullets: [
        "One row per response, one column per field",
        "Submitted-at timestamp in every row",
        "Duplicate-label disambiguation (Notes, Notes (2)…)",
        "Content-Disposition header triggers browser save dialog",
      ],
    },
  ];

  return (
    <section id="features" className="bg-gradient-to from-sky-400 via-zinc-950 
                        to-black-900 py-20 border-t border-zinc-700">
      <div className="max-w-7xl mx-auto px-6">
        <SectionHeading
          eyebrow="What you get"
          title="Everything Your Survey Team Needs"
          subtitle="From voice capture to analytics export — VoxForm AI covers the full data-collection lifecycle."
        />
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f) => (
            <Card key={f.title} className="flex flex-col gap-4 bg-zinc-950">
              <div className="bg-zinc-950">
                <IconCircle icon={f.icon} gradient={`bg-gradient-to-br ${f.gradient}`} />
                <div className="flex justify-center items-center gap-2 mb-3">
                  <span className="font-bold text-slate-200 text-2xl">{f.title}</span>
                </div>
                <Badge color={f.badge.color}>{f.badge.label}</Badge>
              </div>
              <span className="text-slate-500 text-xl leading-relaxed">{f.body}</span>
              <ul className="space-y-1.5 mt-auto">
                {f.bullets.map((b) => (
                  <li key={b} className="flex items-start gap-2 text-xs text-slate-600">
                    <span className="text-emerald-500 mt-0.5 shrink-0">✓</span>
                    {b}
                  </li>
                ))}
              </ul>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}

/** ── 5. VOICE PIPELINE DEEP-DIVE ── */
function PipelineDeepDiveSection() {
  return (
    <section className="bg-gradient-to from-slate-900 to-blue-950 text-white py-24 
                        border-t border-zinc-700">
      <div className="max-w-7xl mx-auto px-6">
        <SectionHeading
          eyebrow="Under the hood"
          title="The Voice-to-Form Pipeline"
          subtitle="Three interfaces, three responsibilities, zero coupling."
        />

        <div className="grid md:grid-cols-3 gap-12">
          {[
            {
              icon: "💾",
              title: "AudioStorage",
              subtitle: "Where bytes live",
              desc: "The browser sends a WebM audio blob via multipart POST. FastAPI writes it to disk (LocalAudioStorage) with a UUID filename to prevent collisions and path-traversal attacks. Future: swap to S3AudioStorage without touching the transcriber.",
              tags: ["UUID filenames", "LocalAudioStorage", "Interface-swappable"],
              color: "blue",
            },
            {
              icon: "🔊",
              title: "Transcriber",
              subtitle: "Audio → Text",
              desc: "FasterWhisperTranscriber (or the Groq Whisper API) converts the audio file to a plain text transcript. The model is lazy-loaded and cached per process — so the first request pays the cold-start cost; all subsequent ones are instant.",
              tags: ["Groq API", "Whisper large-v3", "50+ languages"],
              color: "violet",
            },
            {
              icon: "🧠",
              title: "FieldExtractor",
              subtitle: "Text → Structured JSON",
              desc: "OpenAIFieldExtractor (configured for Groq's LLM endpoint) receives the transcript alongside the form's field schema and returns a JSON array of {field_id, value, confidence} objects. Hallucinated field IDs are silently dropped.",
              tags: ["Groq LLaMA 3", "temp=0", "Confidence scores"],
              color: "emerald",
            },
          ].map((item) => {
            const border = {
              blue: "border-blue-500/30 bg-blue-500/10",
              violet: "border-violet-500/30 bg-violet-500/10",
              emerald: "border-emerald-500/30 bg-emerald-500/10",
            }[item.color];
            const tagColor = {
              blue: "bg-blue-500/20 text-blue-300",
              violet: "bg-violet-500/20 text-violet-300",
              emerald: "bg-emerald-500/20 text-emerald-300",
            }[item.color];

            return (
              <div key={item.title} className={`rounded-2xl border ${border} p-6 flex flex-col gap-4`}>
                <div className="text-4xl">{item.icon}</div>
                <div>
                  <h2 className="font-bold text-white text-lg">{item.title}</h2>
                  <span className="border rounded-xl p-1 text-lg/12 text-slate-400">{item.subtitle}</span>
                </div>
                <span className="text-xl text-slate-300 leading-relaxed flex-1">{item.desc}</span>
                <div className="flex flex-wrap gap-2">
                  {item.tags.map((t) => (
                    <span key={t} className={`text-xs px-2.5 py-1 rounded-full font-medium ${tagColor}`}>
                      {t}
                    </span>
                  ))}
                </div>
              </div>
            );
          })}
        </div>

        {/* Pipeline arrow diagram */}
        <div className="mt-12 flex flex-wrap items-center justify-center gap-2 text-xl">
          {[
            { label: "Browser", sub: "MediaRecorder", icon: "🎤" },
            null,
            { label: "FastAPI", sub: "POST /api/voice/…", icon: "⚡" },
            null,
            { label: "AudioStorage", sub: "saves to disk", icon: "💾" },
            null,
            { label: "Transcriber", sub: "Groq Whisper", icon: "🔊" },
            null,
            { label: "FieldExtractor", sub: "Groq LLM", icon: "🧠" },
            null,
            { label: "React UI", sub: "pre-fills fields", icon: "✍️" },
          ].map((item, i) =>
            item === null ? (
              <div key={i} className="text-slate-500 text-xl">→</div>
            ) : (
              <div key={i} className="flex flex-col items-center bg-zinc-950 border border-white
                                      rounded-xl px-4 py-2.5">
                <span className="text-2xl mb-0.5">{item.icon}</span>
                <span className="font-semibold text-white text-2xl">{item.label}</span>
                <span className="text-slate-400 text-sm">{item.sub}</span>
              </div>
            )
          )}
        </div>
      </div>
    </section>
  );
}

/** ── 6. TECH STACK ── */
function TechStackSection() {
  const groups = [
    {
      title: "Frontend",
      icon: "🖥️",
      items: [
        { name: "React 19", category: "UI Library", icon: "⚛️", color: "blue" },
        { name: "Next.js", category: "Dev Server / SSR", icon: "▲", color: "slate" },
        // { name: "React Router v6", category: "Client-side Routing", icon: "🔀", color: "red" },
        { name: "Tailwind CSS", category: "Utility-first Styling", icon: "🎨", color: "teal" },
        { name: "SurveyJS", category: "Form Builder Engine", icon: "📋", color: "orange" },
        // { name: "Chart.js / react-chartjs-2", category: "Analytics Charts", icon: "📊", color: "purple" },
      ],
    },
    {
      title: "Backend",
      icon: "⚙️",
      items: [
        { name: "Python FastAPI", category: "REST API Framework", icon: "🐍", color: "green" },
        { name: "SQLAlchemy 2", category: "ORM / Query Builder", icon: "🗄️", color: "orange" },
        { name: "MySQL", category: "Relational Database", icon: "🐬", color: "blue" },
        { name: "PyJWT + bcrypt", category: "Auth / Password Hashing", icon: "🔒", color: "slate" },
        { name: "Pydantic v2", category: "Data Validation / DTOs", icon: "✅", color: "purple" },
        { name: "Uvicorn", category: "ASGI Server", icon: "🚀", color: "teal" },
      ],
    },
    {
      title: "AI & Voice",
      icon: "🤖",
      items: [
        { name: "Groq API", category: "LPU Inference Provider", icon: "⚡", color: "yellow" },
        { name: "Whisper AI", category: "Speech-to-Text Model", icon: "🔊", color: "green" },
        { name: "GPT / LLaMA 3", category: "Field Extraction LLM", icon: "🧠", color: "purple" },
        { name: "MediaRecorder API", category: "Browser Audio Capture", icon: "🎤", color: "red" },
      ],
    },
  ];

  return (
    <section id="tech-stack" className="py-24 border-t border-zinc-700">
      <div className="max-w-7xl mx-auto px-6">
        <SectionHeading
          eyebrow="Built with"
          title="Technology Stack"
          subtitle="Modern, battle-tested technologies chosen for performance, developer ergonomics, and long-term maintainability."
        />

        <div className="space-y-10">
          {groups.map((group) => (
            <div key={group.title}>
              <div className="flex items-center gap-2 mb-4">
                <span className="text-3xl">{group.icon}</span>
                <h2 className="text-lg font-bold text-slate-800">{group.title}</h2>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
                {group.items.map((item) => (
                  <TechPill key={item.name} {...item} />
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Architecture diagram summary */}
        <div className="mt-14 bg-zinc-950 rounded-2xl border border-slate-200 p-8">
          <span className="text-4xl font-bold text-slat-200 mb-6 text-center">
            System Architecture Overview
          </span>
          <div className="grid sm:grid-cols-3 gap-6 text-center text-sm mt-8">
            {[
              {
                layer: "Presentation Layer",
                items: ["React 18 + Next.js", "React Router v6", "SurveyJS Form Builder", "Chart.js Dashboards"],
                color: "blue",
                icon: "🖥️",
              },
              {
                layer: "Application Layer",
                items: ["FastAPI REST API", "JWT HttpOnly Cookies", "Dependency Injection", "Repository Pattern"],
                color: "emerald",
                icon: "⚙️",
              },
              {
                layer: "Data & AI Layer",
                items: ["MySQL + SQLAlchemy", "Groq Whisper API", "Groq LLM API", "bcrypt Password Hashing"],
                color: "violet",
                icon: "🗄️",
              },
            ].map((layer) => {
              const bg = { blue: "bg-blue-450 border-blue-200", emerald: "bg-emerald-450 border-emerald-200", violet: "bg-violet-450 border-violet-200" }[layer.color];
              const text = { blue: "text-blue-700", emerald: "text-emerald-700", violet: "text-violet-700" }[layer.color];
              return (
                <div key={layer.layer} className={`rounded-xl border bg-[#020c0e] p-5`}>
                  <div className="text-3xl mb-3">{layer.icon}</div>
                  <h2 className={`font-bold text-sm ${text}`}>{layer.layer}</h2>
                  <ul className="space-y-1.5">
                    {layer.items.map((item) => (
                      <li key={item} className="text-sm text-slate-400 rounded-lg px-3 py-1.5 border border-slate-100">
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}

/** ── 7. SECURITY ── */
function SecuritySection() {
  const points = [
    {
      icon: "🍪",
      title: "HttpOnly Session Cookies",
      desc: "The JWT is stored exclusively in an HttpOnly, SameSite=Lax cookie. JavaScript can never read it, eliminating the most common XSS-based token theft vector that plagues localStorage-based auth.",
    },
    {
      icon: "🏢",
      title: "Org-level Data Isolation",
      desc: "Every database query filters by org_id at the SQL level inside the repository layer — not in service logic or route handlers. Org A cannot see Org B's forms or responses even by guessing UUIDs.",
    },
    {
      icon: "🎭",
      title: "Role-based Access Control",
      desc: "Two roles (Org Admin, Respondent) are enforced via FastAPI Depends(require_role()) decorators on each route. The role is embedded in the JWT so authorization decisions don't need a database lookup.",
    },
    {
      icon: "🔑",
      title: "bcrypt Password Hashing",
      desc: "Passwords are hashed with bcrypt at work factor 12 (~200ms per hash). The plaintext password is never stored or logged. A random salt is generated per hash, preventing rainbow-table attacks.",
    },
    {
      icon: "📨",
      title: "Invite-only Registration",
      desc: "There is no public signup route. New accounts are created only by Org Admins issuing invite tokens, or by a privileged seed script. Each token is single-use, expires in 7 days, and carries a fixed role.",
    },
    {
      icon: "✅",
      title: "Server-side Input Validation",
      desc: "Every API request is validated by Pydantic v2 schemas before reaching business logic. Choice-field answers are checked against declared options; number fields must parse as float; required fields are enforced.",
    },
  ];

  return (
    <section id="security" className="bg-white py-24">
      <div className="max-w-6xl mx-auto px-6">
        <SectionHeading
          eyebrow="Built-in security"
          title="Security Architecture"
          subtitle="Security is a first-class concern, not an afterthought — enforced at every layer of the stack."
        />
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {points.map((p) => (
            <Card key={p.title}>
              <div className="text-3xl mb-3">{p.icon}</div>
              <h3 className="font-bold text-slate-900 mb-2 text-sm">{p.title}</h3>
              <p className="text-sm text-slate-500 leading-relaxed">{p.desc}</p>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}

/** ── 8. ROLE SYSTEM ── */
function RoleSystemSection() {
  return (
    <section className="py-24 border-t border-zinc-600">
      <div className="max-w-7xl mx-auto px-6">
        <SectionHeading
          eyebrow="User roles"
          title="Org Admin vs Respondent"
          subtitle="Two clearly differentiated roles with purpose-built capabilities."
        />

        <div className="max-w-5xl mx-auto px-6 grid md:grid-cols-2 gap-8">
          {/* Org Admin */}
          <div className="bg-white rounded-2xl border border-amber-200 shadow-sm overflow-hidden">
            <div className="bg-gradient-to-r from-sky-400 to-zinc-900 px-6 py-4 items-center gap-3">
              {/* <span className="text-2xl">👑</span> */}
                <h2 className="font-black text-lg">👑 Org Admin</h2>
                <p className="text-amber-100 text-xs">Full control over the organisation</p>
            </div>
            <div className="p-6 space-y-3 bg-zinc-950">
              {[
                ["📋", "Create, edit & delete forms via SurveyJS builder"],
                ["📚", "Browse and clone global form templates"],
                ["📨", "Invite new Org Admins and Respondents"],
                ["👥", "View & manage all org members"],
                ["📊", "Access analytics dashboard for all forms"],
                ["📥", "Export any form's responses as CSV"],
                ["🏗️", "Configure form logic, branching, and multi-pages"],
              ].map(([icon, text]) => (
                <div key={text} className="flex items-start gap-3 bg-zinc-950">
                  <span className="text-base text-zinc-200 shrink-0 mt-0.5">{icon}</span>
                  <span className="text-m text-zinc-200 font-calibiri">{text}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Respondent */}
          <div className="bg-white rounded-2xl border border-blue-200 shadow-sm overflow-hidden">
            <div className="bg-gradient-to-r from-zinc-900 to-sky-500 px-6 py-4 items-center gap-3">
              {/* <span className="text-2xl">🎤</span> */}
                <h2 className="font-black text-white text-lg">🎤 Respondent</h2>
                <p className="text-blue-100 text-xs">Focused form-filling experience</p>
            </div>
            <div className="p-6 space-y-3 bg-zinc-950">
              {[
                ["📋", "View all forms in their org"],
                ["🎤", "Voice-fill forms with microphone recording"],
                ["✍️", "Review, correct & submit responses"],
                ["📝", "See the AI-generated transcript for each session"],
                ["🔢", "Manual entry fallback for all field types"],
                ["🔒", "Isolated from other orgs' data (multi-tenant)"],
                ["🚫", "No access to templates, or team management"],
              ].map(([icon, text]) => (
                <div key={text} className="flex items-start gap-3 bg-zinc-950">
                  <span className="text-base text-zinc-200 shrink-0 mt-0.5">{icon}</span>
                  <span className="text-m text-zinc-200 font-calibiri">{text}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Invite flow */}
        <div className="mt-10 bg-gradient-to-t from-sky-400 to-zinc-950 rounded-2xl border 
                        border-zinc-200 py-8 px-1">
          <h2 className="font-bold text-slate-900 mb-5 text-center text-lg">
            Onboarding Flow — How New Members Join
          </h2>
          <div className="flex flex-wrap mt-5 items-center justify-center gap-4 text-sm">
            {[
              { icon: "👑", label: "Admin opens /invite" },
              "→",
              { icon: "📝", label: "Fills name, email, role" },
              "→",
              { icon: "🔗", label: "System generates one-time link" },
              "→",
              { icon: "📤", label: "Admin shares the invite URL" },
              "→",
              { icon: "🔑", label: "Invitee sets password" },
              "→",
              { icon: "✅", label: "Account created, logged in" },
            ].map((item, i) =>
              item === "→" ? (
                <span key={i} className="text-zinc-950 text-2xl font-bold">→</span>
              ) : (
                <div key={i} className="flex flex-col items-center bg-zinc-950 border border-slate-200 rounded-xl px-4 py-2.5 text-center">
                  <span className="text-xl mb-0.5">{item.icon}</span>
                  <span className="text-xs text-slate-200 font-medium leading-snug max-w-[120px]">
                    {item.label}
                  </span>
                </div>
              )
            )}
          </div>
        </div>
      </div>
    </section>
  );
}

/** ── 9. ROADMAP ── */
function RoadmapSection() {
  const phases = [
    {
      phase: "Phase 1",
      status: "Shipped",
      statusColor: "emerald",
      title: "Core Voice Loop",
      items: [
        "Voice recording via browser MediaRecorder",
        "Groq Whisper transcription pipeline",
        "LLM field extraction with confidence scores",
        "Dynamic form pre-filling and manual review",
        "POST /api/forms and response submission",
      ],
    },
    {
      phase: "Phase 2",
      status: "Shipped",
      statusColor: "emerald",
      title: "Multi-tenant Auth & Teams",
      items: [
        "JWT HttpOnly cookie authentication",
        "Org Admin + Respondent RBAC",
        "Invite-only team onboarding",
        "Multi-org data isolation at repository layer",
        "Global form template gallery with clone",
      ],
    },
    {
      phase: "Phase 3",
      status: "Shipped",
      statusColor: "emerald",
      title: "CSV Data Export",
      items: [
        "Org-wide response overview dashboard",
        "Per-form analytics: trend, completion rate, field stats",
        "Chart.js interactive charts",
        "CSV export of form data",
        "Per-field breakdowns: choice bars, number min/avg/max",
      ],
    },
    {
      phase: "Phase 4",
      status: "Planned",
      statusColor: "amber",
      title: "Voice-based Form Generation",
      items: [
        "\"Build me a customer satisfaction survey\" → AI generates the form",
        "LLM designs field labels, types, options, logic from a description",
        "Admin reviews and tweaks the AI-generated form before publishing",
        "SurveyJS JSON schema as the intermediate representation",
      ],
    },
    {
      phase: "Phase 5",
      status: "Planned",
      statusColor: "amber",
      title: "Agentic Post-submission Workflows",
      items: [
        "Auto-trigger workflows after form submission (webhooks, email, CRM)",
        "AI summarises free-text responses and routes to relevant teams",
        "Anomaly detection: flag unusual or inconsistent responses",
        "Integration with Zapier, n8n, Slack, and Google Sheets",
      ],
    },
  ];

  const statusStyle = {
    emerald: "bg-emerald-100 text-emerald-700 border-emerald-200",
    amber: "bg-amber-100 text-amber-700 border-amber-200",
    slate: "bg-slate-100 text-slate-600 border-slate-200",
  };

  return (
    <section id="roadmap" className="py-24 text-white border-t border-zinc-700">
      <div className="max-w-5xl mx-auto px-6">
        <SectionHeading
          eyebrow="What's next"
          title="Product Roadmap"
          subtitle="Three phases shipped. Two transformative phases planned."
        />

        <div className="relative">
          {/* Vertical timeline line */}
          <div className="absolute left-[18px] sm:left-[26px] top-0 bottom-0 w-0.5 bg-slate-700" />

          <div className="space-y-8">
            {phases.map((phase, idx) => (
              <div key={phase.phase} className="relative flex gap-6 sm:gap-8">
                {/* Timeline dot */}
                <div className="shrink-0 relative z-10">
                  <div
                    className={`w-9 h-9 sm:w-[52px] sm:h-[52px] rounded-full border-2 flex items-center justify-center font-black text-xs sm:text-sm
                      ${phase.statusColor === "emerald"
                        ? "bg-emerald-500 border-emerald-400 text-white"
                        : "bg-slate-800 border-slate-600 text-slate-400"
                      }`}
                  >
                    {phase.statusColor === "emerald" ? "✓" : idx + 1}
                  </div>
                </div>

                {/* Card */}
                <div
                  className={`flex-1 rounded-2xl border p-5 sm:p-6 mb-2
                    ${phase.statusColor === "emerald"
                      ? "border-emerald-500/20 bg-emerald-500/5"
                      : "border-slate-700 bg-slate-800/50"
                    }`}
                >
                  <div className="flex flex-wrap items-center gap-3 mb-3">
                    <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">
                      {phase.phase}
                    </span>
                    <span
                      className={`text-xs font-semibold px-2.5 py-0.5 rounded-full border ${statusStyle[phase.statusColor]}`}
                    >
                      {phase.status}
                    </span>
                    <h3 className="font-extrabold text-white text-base w-full sm:w-auto sm:ml-auto">
                      {phase.title}
                    </h3>
                  </div>
                  <ul className="space-y-2">
                    {phase.items.map((item) => (
                      <li key={item} className="flex items-start gap-2.5 text-sm">
                        <span
                          className={`shrink-0 mt-0.5 font-bold ${
                            phase.statusColor === "emerald" ? "text-emerald-400" : "text-slate-500"
                          }`}
                        >
                          {phase.statusColor === "emerald" ? "✓" : "◦"}
                        </span>
                        <span className={phase.statusColor === "emerald" ? "text-slate-300" : "text-slate-500"}>
                          {item}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

/** ── 10. FAQ ── */
function FAQSection() {
  const faqs = [
    {
      question: "Which languages does the voice input support?",
      answer:
        "Groq's Whisper large-v3 model supports over 50 languages including English, Hindi, Spanish, French, Arabic, Mandarin, and more. Language detection is automatic — you don't need to configure anything. The extracted field values are always returned in the English language.",
    },
    {
      question: "How accurate is the field extraction?",
      answer:
        "The LLM field extractor (OpenAI GPT API) operates at temperature 0 for maximum determinism. For structured fields like choice options and numbers, accuracy is very high because the model is given the exact list of valid options. For free-text fields it captures what was said verbatim.",
    },
    {
      question: "Is my data secure? Can one organisation see another's data?",
      answer:
        "Data is fully secured. Tenant isolation is enforced at the SQL query level inside repository classes — every query filters by org_id. Even if a user guesses another org's form UUID, the backend returns 404 because the form's org_id does not match the authenticated user's org_id embedded in their JWT.",
    },
    {
      question: "Can respondents use the form without voice input?",
      answer:
        "Yes. Voice filling is a convenience layer on top of standard HTML form inputs. Respondents can type answers directly into any field at any time. The voice extraction result pre-fills fields but the user can override every value before submitting.",
    },
    {
      question: "How does the invite system work?",
      answer:
        "Org Admins generate one-time invite tokens via the /invite page. Each token encodes the invitee's email, full name, and role. The admin copies the /accept-invite/:token URL and shares it with the invitee however they prefer (email, Slack, etc.). The invitee clicks the link, sets a password, and now can log in with Email and Password. Tokens expire after 7 days and can only be used once.",
    },
    {
      question: "What form types does the SurveyJS builder support?",
      answer:
        "SurveyJS supports 30+ question types including text, number, dropdown, checkbox, radio, matrix, rating, boolean, and more. Forms can have multiple pages.",
    },
    {
      question: "What's planned for next Phase of development — Analytics dashboard & Voice-based form generation?",
      answer:
        "In next phase, an Org Admin will be able to describe a form in plain language ('build me a 10-question patient intake form with name, date of birth, symptoms, and severity ratings') and the LLM will generate a complete SurveyJS JSON schema. The admin reviews and tweaks it in the visual builder before publishing. Also, Org Admin will get insights from collected form data through an exhaustive analytics dashboards.",
    },
  ];

  return (
    <section className="py-24 border-t border-zinc-700">
      <div className="max-w-7xl mx-auto px-6">
        <SectionHeading
          eyebrow="Questions"
          title="Frequently Asked Questions"
          subtitle="Everything you need to know about VoxForm AI."
        />
        <div className="space-y-3">
          {faqs.map((faq) => (
            <AccordionItem key={faq.question} question={faq.question} answer={faq.answer} />
          ))}
        </div>
      </div>
    </section>
  );
}

/** ── 11. CTA FOOTER ── */
function CTASection() {
  return (
    <section className="bg-gradient-to-t from-[#020c0e]_90% to-sky-950 py-20 text-white text-center">
      <div className="max-w-3xl mx-auto px-6">
        <div className="text-7xl mb-5">🎙️</div>
        <h2 className="text-3xl sm:text-4xl font-extrabold mb-4">
          Ready to fill forms at the speed of speech?
        </h2>
        <p className="text-blue-100 text-lg mb-8 leading-relaxed">
          VoxForm AI brings together voice AI, a powerful form builder, and a
          secure multi-tenant platform in one streamlined tool. <br></br><br></br>Get your organisation
          set up in minutes.
        </p>
        <div className="flex flex-wrap items-center justify-center gap-4">
          <Link
            href="/" 
            aria-label="Get Started with VoxForm AI"
            className="px-8 py-3.5 bg-zinc-950 text-white font-bold rounded-xl border border-slate
                      hover:bg-blue-50 hover:text-zinc-950 transition-colors shadow-lg text-m"
          >
            Get Started →
          </Link>
          <Link
            href="#how-it-works"
            className="px-8 py-3.5 bg-white/15 border border-white/30 text-white font-bold
                       rounded-xl hover:bg-white/25 transition-colors text-m"
          >
            Watch the Pipeline
          </Link>
        </div>

        {/* Mini tech badges */}
        <div className="flex flex-wrap items-center justify-center gap-3 mt-10 opacity-60">
          {["⚛️ React", "🐍 FastAPI", "⚡ OpenAI GPT", "🎤 Whisper", "🔒 JWT", "📋 SurveyJS"].map((t) => (
            <span key={t} className="text-xs bg-white/10 border border-white/20 rounded-full px-3 py-1">
              {t}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}

/** ── FOOTER ── */
function FooterAbout() {
  return (
    <footer className="bg-slate-900 text-slate-400 py-10 text-center text-sm">
      <div className="max-w-6xl mx-auto px-6">
        <div className="flex items-center justify-center gap-2 mb-4">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-blue-400 to-violet-500 flex items-center justify-center">
            <span className="text-sm">🎙️</span>
          </div>
          <span className="font-black text-white text-lg">
            Vox<span className="text-blue-400">Form</span>
            <span className="text-xs text-blue-400/70 ml-1">AI</span>
          </span>
        </div>
        <p className="max-w-lg mx-auto mb-4 text-slate-500 leading-relaxed">
          Voice-powered survey forms for organisations that move fast.
          Built with React · FastAPI · Groq · SurveyJS · MySQL.
        </p>
        <p className="text-slate-600 text-xs">
          © {new Date().getFullYear()} VoxForm AI · All rights reserved
        </p>
      </div>
    </footer>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Root Page Export
// ─────────────────────────────────────────────────────────────────────────────

/**
 * AboutPage — the complete VoxForm AI about page.
 *
 * Add this to your React Router config:
 *   <Route path="/about" element={<AboutPage />} />
 *
 * All sections are self-contained. Anchor links (#how-it-works, #features,
 * #tech-stack, #security, #roadmap) work with standard browser hash navigation.
 */
export default function AboutPage() {
  useEffect(() => {
    // Setting Tab Title
    document.title = 'About | VoxForm AI';
  }, []);

  return (
    <div className="font-sans antialiased">
      <HeroSection />
      <StatsBar />
      <HowItWorksSection />
      <CoreFeaturesSection />
      <PipelineDeepDiveSection />
      <TechStackSection />

      {/* <SecuritySection /> */}

      <RoleSystemSection />

      {/* <RoadmapSection /> */}

      <FAQSection />
      <CTASection />

      {/* <FooterAbout /> */}
      <Footer />

    </div>
  );
}

