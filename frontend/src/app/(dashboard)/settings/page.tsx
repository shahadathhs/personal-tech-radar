import { SettingsForm } from "@/components/settings-form";

export const metadata = { title: "Settings · Tech Radar" };

export default function SettingsPage() {
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Settings</h1>
        <p className="text-sm text-muted-foreground">
          Your profile drives relevance scoring and digest timing.
        </p>
      </div>
      <SettingsForm />
    </div>
  );
}
