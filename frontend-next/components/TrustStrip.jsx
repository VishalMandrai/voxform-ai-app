/*
|--------------------------------------------------------------------------
| Trust Strip
|--------------------------------------------------------------------------
| Later these can become customer logos.
|--------------------------------------------------------------------------
*/

export default function TrustStrip() {

  const items = [
    "Voice Recognition", "|",
    "GPT Inference", "|",
    "MySQL", "|",
    "FastAPI-Next.JS", "|",
    "JWT User Authentication"
  ];

  return (

    <section className="mt-18 border-y border-zinc-800">
      <div className="mx-auto flex max-w-7xl flex-wrap justify-center gap-5 py-8 text-zinc-400">
        {items.map((item, index) => (
          <div key={index}>
            <p>{item}</p>
          </div>
        ))}
      </div>
    </section>

  );

}