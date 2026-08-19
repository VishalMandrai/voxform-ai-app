'use client'

import { Mic } from "lucide-react";

/*
|--------------------------------------------------------------------------
| Top Navigation
|--------------------------------------------------------------------------
*/

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 backdrop-blur-lg bg-zinc-950/70 border-b border-zinc-800">

      <div className="mx-auto flex h-20 max-w-7xl items-center justify-between px-8">

        {/* Logo */}

        <div className="flex items-center gap-3">

          <div className="rounded-xl bg-sky-500 p-3 shadow-lg shadow-sky-500/40">
            <Mic size={20} />
          </div>

          <div>

            <h2 className="text-xl font-bold">
              VoxForm AI
            </h2>

            <p className="text-xs text-zinc-400">
              Voice Powered Forms
            </p>

          </div>

        </div>

        {/* Navigation */}

        <nav className="hidden gap-10 md:flex">

          <a href="#" className="text-zinc-300 hover:text-sky-400">
            Features
          </a>

          <a href="#" className="text-zinc-300 hover:text-sky-400">
            Workflow
          </a>

          <a href="#" className="text-zinc-300 hover:text-sky-400">
            Pricing
          </a>

        </nav>

        {/* Login */}

        {/* <button className="rounded-xl border border-sky-500 px-6 py-2 text-sky-400 transition hover:bg-sky-500 hover:text-white">

          Login

        </button> */}

      </div>

    </header>
  );
}