export type Prediction = {
  label: string;
  confidence?: number | null;
  explanation: string;
  top_features: string[];
};

export type EvaluationMetrics = {
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
};

export type ModelComparison = EvaluationMetrics & {
  model: string;
};

export type ModelInfo = {
  dataset?: {
    source?: string;
    dataset_type?: string;
    rows?: number;
    spam_count?: number;
    ham_count?: number;
  };
  selected_model?: string;
  evaluation?: Partial<EvaluationMetrics>;
  comparison?: ModelComparison[];
};

export type KeywordInsights = {
  spam_terms: string[];
  ham_terms: string[];
};

export type HistoryItem = {
  timestamp: string;
  label: string;
  message_preview: string;
};
