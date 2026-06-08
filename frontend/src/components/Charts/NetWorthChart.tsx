import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { useTheme } from "../../context/ThemeContext";

interface DataPoint {
  date: string;
  balance: number;
}

interface Props {
  data: DataPoint[];
}

export default function NetWorthChart({ data }: Props) {
  const { theme } = useTheme();
  const strokeColor = theme === "dark" ? "#9ca3af" : "#6b7280";

  if (!data.length) {
    return (
      <div className="flex h-64 items-center justify-center text-gray-400">
        No data available
      </div>
    );
  }

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke={strokeColor} opacity={0.3} />
          <XAxis dataKey="date" stroke={strokeColor} tick={{ fontSize: 12 }} />
          <YAxis stroke={strokeColor} tick={{ fontSize: 12 }} />
          <Tooltip
            contentStyle={{
              backgroundColor: theme === "dark" ? "#1f2937" : "#fff",
              border: "1px solid #374151",
              color: theme === "dark" ? "#f9fafb" : "#111827",
            }}
          />
          <Line
            type="monotone"
            dataKey="balance"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
