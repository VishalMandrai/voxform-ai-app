import { FaMicrophoneAlt } from "react-icons/fa";
import { RiMic2AiFill } from "react-icons/ri";


export default function CTASection() {

  return (

    <section className="mx-auto max-w-7xl px-8 mt-30">
        <div className="max-w-5xl mx-auto px-6">
        <div className="text-7xl mb-5 inline-flex text-slate-200"><RiMic2AiFill /></div>
        <h2 className="text-3xl sm:text-4xl font-extrabold mb-4">
          Ready to fill forms at the speed of speech?
        </h2>
        <p className="text-blue-100 text-lg mb-8 leading-relaxed">
          VoxForm AI brings together voice AI, a powerful form builder, and a
          secure multi-tenant platform in one streamlined tool.
        </p>
        <div className="flex flex-wrap items-center justify-center gap-4">
          <a
            href="#main-wrapper"
            className="px-8 py-3.5 bg-zinc-950 text-white font-bold rounded-xl border border-slate
                      hover:bg-blue-50 hover:text-zinc-950 transition-colors shadow-lg text-m"
          >
            Get Started →
          </a>
        </div>

        {/* Mini tech badges */}
        <div className="flex flex-wrap items-center justify-center gap-5 mt-10 mb-30">
          {["⚛️ React", "🐍 FastAPI", "⚡ OpenAI GPT", "🎤 Whisper", "🔒 JWT", "📋 SurveyJS"].map((t) => (
            <span key={t} className="text-lg text-white bg-white/10 border border-white/30 
                                    rounded-full px-3 py-1 transition-colors shadow-lg">
              {t}
            </span>
          ))}
        </div>
      </div>
    </section>

  )
}