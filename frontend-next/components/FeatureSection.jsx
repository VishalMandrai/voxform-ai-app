import {
    BrainCircuit,
    ShieldCheck,
    LayoutDashboard
} from "lucide-react";

import { LuMicVocal } from "react-icons/lu";

/*
|--------------------------------------------------------------------------
| Product Features
|--------------------------------------------------------------------------
*/

const features = [

{
title:"Voice Input",
icon:<LuMicVocal size={32}/>,
text:"Fill forms by simply speaking."
},

{
title:"LLM Powered",
icon:<BrainCircuit size={32}/>,
text:"Context aware field prediction."
},

{
title:"Form Builder",
icon:<LayoutDashboard size={32}/>,
text:"Create forms and manage them."
},

{
title:"User Security",
icon:<ShieldCheck size={32}/>,
text:"Authentication and encrypted storage."
}

];

export default function FeatureSection(){
    return(
    <section className="mx-auto max-w-7xl px-8 py-5">
        <h1 className="text-center text-4xl font-bold">
            Powerful Features
        </h1>
        <div className="mt-8 grid gap-6 md:grid-cols-2 xl:grid-cols-4">
            {features.map((feature)=>(
        <div
        key={feature.title}
        className="rounded-3xl border border-zinc-800 bg-zinc-900 p-4 transition 
                    hover:-translate-y-2 hover:border-sky-500"
        >
            <div className = "inline-flex items-center gap-x-2">
                <div className="text-sky-400">
                    {feature.icon}
                </div>

                <h3 className="text-xl font-semibold">
                    {feature.title}
                </h3>
            </div>

            <p className="mt-4 text-zinc-400 text-sm">
                {feature.text}
            </p>

        </div>

))}

</div>

</section>

);

}