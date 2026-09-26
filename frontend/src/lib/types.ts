export type DigestItem = {
  id: string;
  position: number;
  section: string;
  category: string | null;
  final_score: number;
  title: string;
  url: string;
  source_name: string | null;
  summary: string;
  why_it_matters: string | null;
  why_user_should_care: string | null;
  recommended_action: string;
};

export type Digest = {
  id: string;
  digest_date: string;
  status: string;
  reading_time_minutes: number;
  generated_at: string | null;
  sent_at: string | null;
  items: DigestItem[];
};

export type DigestSummary = {
  id: string;
  digest_date: string;
  status: string;
  reading_time_minutes: number;
  item_count: number;
};

export type Source = {
  id: string;
  name: string;
  source_type: string;
  url: string;
  config: Record<string, unknown>;
  quality_weight: number;
  rate_limit_seconds: number;
  enabled: boolean;
  last_collected_at: string | null;
};

export type Interest = {
  id: string;
  name: string;
  parent_name: string | null;
  weight: number;
  enabled: boolean;
};

export type Profile = {
  email: string;
  timezone: string;
  role: string;
  experience_level: string;
  digest_time: string;
  digest_length: string;
  excluded_topics: string[];
  preferred_sources: string[];
  interests: Interest[];
};

export type SavedItem = {
  content_item_id: string;
  title: string;
  url: string;
  source_name: string | null;
  saved_at: string;
};
