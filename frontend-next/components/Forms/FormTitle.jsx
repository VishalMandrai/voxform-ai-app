export default function FormTitle({ title, description }) {
    return (
        <div className="border-b border-[#13333d] px-2 py-2">
            <div className="mb-5 items-center">
                <div>
                    <h1 className="mt-2 text-3xl font-bold text-slate-800">
                        {title}
                    </h1>
                    <p className="mt-1 text-slate-500">
                        {description}
                    </p>
                </div>
            </div>

        </div>
    );
}