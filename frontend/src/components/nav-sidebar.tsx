"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Bookmark, Radio, Rss, Settings, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";
import { BackendStatus } from "@/components/backend-status";

const NAV_ITEMS = [
  { href: "/", label: "Today", icon: Radio },
  { href: "/sources", label: "Sources", icon: Rss },
  { href: "/interests", label: "Interests", icon: Sparkles },
  { href: "/saved", label: "Saved", icon: Bookmark },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex w-56 shrink-0 flex-col border-r bg-sidebar">
      <div className="flex h-14 items-center gap-2 border-b px-4">
        <span className="text-lg">🧠</span>
        <div className="leading-tight">
          <div className="text-sm font-semibold">Tech Radar</div>
          <div className="text-xs text-muted-foreground">daily briefing</div>
        </div>
      </div>
      <nav className="flex-1 space-y-1 p-3">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors",
                active
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-foreground",
              )}
            >
              <Icon className="size-4" />
              {label}
            </Link>
          );
        })}
      </nav>
      <div className="border-t p-3">
        <BackendStatus />
      </div>
    </aside>
  );
}
