import { Mic, BrainCircuit, ClipboardCheck } from "lucide-react";

/*
|--------------------------------------------------------------------------
| Three-step workflow
|--------------------------------------------------------------------------
*/

const steps = [
  {
    icon: <Mic size={32}/>,
    title: "Speak",
    text: "Talk naturally instead of typing."
  },
  {
    icon: <BrainCircuit size={32}/>,
    title: "AI Understands",
    text: "LLMs map your speech into structured fields."
  },
  {
    icon: <ClipboardCheck size={32}/>,
    title: "Done",
    text: "Review and submit your completed form."
  }
];

export default function HowItWorks() {

  return (

    <section className="mx-auto max-w-7xl px-8 py-12">

      <h1 className="text-center text-4xl font-bold">
        How VoxForm Works
      </h1>

      <div className="mt-8 grid gap-6 md:grid-cols-3">
        {steps.map((step) => (
          <div
            key={step.title}
            className="rounded-3xl border border-zinc-800 bg-zinc-900 p-8 hover:border-sky-500 
                      hover:-translate-y-2"
          >
            <div className = "inline-flex gap-x-2">
              <div className="text-sky-400">
                {step.icon}
              </div>

              <h3 className="mx-auto text-2xl font-bold">
                {step.title}
              </h3>
            </div>

            <p className="mt-4 text-zinc-400">
              {step.text}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}