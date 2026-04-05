import 'package:flutter/material.dart';

class AiInsightLine extends StatelessWidget {
  final Future<String> insightFuture;

  const AiInsightLine({Key? key, required this.insightFuture}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<String>(
      future: insightFuture,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          // Shimmer loading line
          return Container(
            margin: const EdgeInsets.fromLTRB(16, 8, 16, 0),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFF1C2128),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: const Color(0xFF0A7A6E).withOpacity(0.1)),
            ),
            child: Row(
              children: [
                const SizedBox(
                  width: 14,
                  height: 14,
                  child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFF0A7A6E)),
                ),
                const SizedBox(width: 8),
                Text(
                  'Computing mathematical bounds...',
                  style: TextStyle(color: const Color(0xFF8B949E).withOpacity(0.5), fontSize: 13),
                ),
              ],
            ),
          );
        }

        final insight = snapshot.data ?? '';
        if (insight.isEmpty) return const SizedBox.shrink();

        return Container(
          margin: const EdgeInsets.fromLTRB(16, 8, 16, 0),
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: const Color(0xFF1C2128),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(
              color: const Color(0xFF0A7A6E).withOpacity(0.3),
            ),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('🤖 ', style: TextStyle(fontSize: 14)),
              Expanded(
                child: Text(
                  insight,
                  style: const TextStyle(
                    color: Color(0xFFB0B8C4),
                    fontSize: 13,
                    height: 1.4,
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}
