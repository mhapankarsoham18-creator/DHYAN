import 'package:flutter/material.dart';
import 'package:mobile_app/core/services/ai_service.dart';

// ==========================================
// Weekly Report Card Widget
// ==========================================
class WeeklyReportCard extends StatelessWidget {
  final Future<String> reportFuture;
  final String title;
  final IconData icon;

  const WeeklyReportCard({
    Key? key,
    required this.reportFuture,
    required this.title,
    required this.icon,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF30363D)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: const Color(0xFF58A6FF), size: 20),
              const SizedBox(width: 8),
              Text(
                title,
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          FutureBuilder<String>(
            future: reportFuture,
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const Center(
                  child: Padding(
                    padding: EdgeInsets.all(16.0),
                    child: CircularProgressIndicator(strokeWidth: 2),
                  ),
                );
              }
              return Text(
                snapshot.data ?? 'Report unavailable.',
                style: const TextStyle(
                  color: Color(0xFFB0B8C4),
                  height: 1.5,
                  fontSize: 14,
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}

// ==========================================
// Pattern Explainer Bottom Sheet Helper
// ==========================================
Future<void> showPatternExplainer(
  BuildContext context,
  String patternName,
  String symbol,
  AiService aiService,
) async {
  showModalBottomSheet(
    context: context,
    backgroundColor: const Color(0xFF161B22),
    shape: const RoundedRectangleBorder(
      borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
    ),
    builder: (_) => FutureBuilder<String>(
      future: aiService.explainPattern(
        patternName: patternName,
        symbol: symbol,
      ),
      builder: (context, snapshot) {
        return Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                patternName.toUpperCase(),
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 4),
              const Text(
                'Pattern Dictionary',
                style: TextStyle(color: Color(0xFF8B949E), fontSize: 13),
              ),
              const SizedBox(height: 16),
              if (snapshot.connectionState == ConnectionState.waiting)
                const Center(
                  child: CircularProgressIndicator(
                    color: Color(0xFF0A7A6E),
                    strokeWidth: 2,
                  ),
                )
              else
                Text(
                  snapshot.data ?? 'Explanation unavailable.',
                  style: const TextStyle(
                    color: Color(0xFFB0B8C4),
                    fontSize: 15,
                    height: 1.6,
                  ),
                ),
              const SizedBox(height: 24),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.black.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: const Row(
                  children: [
                    Icon(Icons.info_outline, color: Color(0xFF8B949E), size: 16),
                    SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        "Educational definition only. Not investment advice.",
                        style: TextStyle(color: Color(0xFF8B949E), fontSize: 12),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    ),
  );
}
