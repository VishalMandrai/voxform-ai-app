'use client'

// Status Grid Card:
export default function StatsGrid(props) {
  const stats = [
    ["Forms", props.total_forms],
    ["Responses", props.total_responses],
    ["Members", props.total_members],
    ["Invitations", props.total_invites],
  ];


  return (
    <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">

      {stats.map(([label, value]) => (

        <div key={label} className="rounded-2xl border border-zinc-800 bg-zinc-900 p-6 transition 
                                    hover:bg-zinc-800">

          <p className="text-zinc-400 font-semibold">
            {label}
          </p>

          <h2 className="mt-3 text-3xl font-bold">
            {value}
          </h2>

        </div>
      ))}
    </div>
  );
}