import { ArrowRight } from "lucide-react";

import { useRouter } from "next/navigation";

/*
|--------------------------------------------------------------------------
| Marketing Content
|--------------------------------------------------------------------------
*/

export default function HeroContent() {
  const navigation = useRouter()
  
  return (

    <div>

      <div className="inline-flex rounded-full border border-sky-500/40 bg-sky-500/10 px-5 py-2 text-m 
                      text-sky-300">
        AI Powered Voice Forms
      </div>

      <h1 className="mt-8 text-6xl font-black leading-tight">
        Stop Typing.
        <br />
        Start
        <span className="text-sky-400">
          {" "}Speaking.
        </span>
      </h1>

      <p className="mt-8 max-w-xl text-lg leading-8 text-zinc-400">
        VoxForm AI lets you complete forms naturally using your voice. <br></br><br></br>
        Our AI understands context, fills fields intelligently,
        and makes digital paperwork effortless.
      </p>

      <div className="mt-10 inline-flex gap-8">
        {/* <button className="flex items-center gap-2 rounded-xl bg-sky-500 px-5 py-4 font-semibold 
                          text-zinc-950 shadow-xl shadow-sky-500/10 hover:bg-sky-400">
          Get Started
          <ArrowRight size={18}/>
        </button> */}

        <button className="rounded-xl border border-zinc-200 px-7 py-4 hover:border-sky-500
                          font-black text-xl"
                          onClick={() => navigation.push("/about")}>
          Learn More
        </button>
      </div>
    </div>
  );

}