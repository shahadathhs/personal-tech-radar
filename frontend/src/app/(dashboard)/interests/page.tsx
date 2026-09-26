import { InterestsView } from "@/components/interests-view";

export const metadata = { title: "Interests · Tech Radar" };

export default function InterestsPage() {
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Interests</h1>
        <p className="text-sm text-muted-foreground">
          What the relevance engine scores content against. Parent topics can have children.
        </p>
      </div>
      <InterestsView />
    </div>
  );
}
