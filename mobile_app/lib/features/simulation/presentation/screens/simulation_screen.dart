import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile_app/core/theme/app_theme.dart';
import 'package:mobile_app/core/network/dio_client.dart';

/// Simulation mode controller
class SimulationState {
  final bool isActive;
  final String remainingTime;
  final double virtualBalance;
  final bool isLoading;
  final String? error;

  const SimulationState({
    this.isActive = false,
    this.remainingTime = '',
    this.virtualBalance = 0.0,
    this.isLoading = false,
    this.error,
  });

  SimulationState copyWith({
    bool? isActive,
    String? remainingTime,
    double? virtualBalance,
    bool? isLoading,
    String? error,
  }) {
    return SimulationState(
      isActive: isActive ?? this.isActive,
      remainingTime: remainingTime ?? this.remainingTime,
      virtualBalance: virtualBalance ?? this.virtualBalance,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

class SimulationController extends Notifier<SimulationState> {
  @override
  SimulationState build() {
    _checkStatus();
    return const SimulationState();
  }

  Future<void> _checkStatus() async {
    try {
      final resp = await dioClient.dio.get('/api/v1/auth/me');
      final data = resp.data;
      final isActive = data['simulation_active'] == true;
      final balance = (data['virtual_balance'] ?? 0.0).toDouble();
      state = state.copyWith(isActive: isActive, virtualBalance: balance);
    } catch (_) {}
  }

  Future<void> startSimulation() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final resp = await dioClient.dio.post('/api/v1/auth/simulation/start');
      final data = resp.data;
      state = state.copyWith(
        isActive: data['simulation_active'] == true,
        virtualBalance: (data['virtual_balance'] ?? 250000.0).toDouble(),
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }
}

final simulationControllerProvider = NotifierProvider<SimulationController, SimulationState>(
  SimulationController.new,
);

/// Simulation Screen UI
class SimulationScreen extends ConsumerWidget {
  const SimulationScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final sim = ref.watch(simulationControllerProvider);
    final controller = ref.read(simulationControllerProvider.notifier);

    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        leading: IconButton(
          onPressed: () => Scaffold.of(context).openDrawer(),
          icon: const Icon(Icons.menu_rounded, size: 22),
        ),
        title: const Text('Practice Mode'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        physics: const BouncingScrollPhysics(),
        child: sim.isActive
            ? _buildActiveSimulation(sim)
            : _buildWelcomeScreen(sim, controller),
      ),
    );
  }

  Widget _buildWelcomeScreen(SimulationState sim, SimulationController controller) {
    return Column(
      children: [
        const SizedBox(height: 40),

        // Hero illustration
        Container(
          width: 100,
          height: 100,
          decoration: BoxDecoration(
            gradient: AppTheme.primaryGradient,
            shape: BoxShape.circle,
            boxShadow: [
              BoxShadow(
                color: AppTheme.primary.withValues(alpha: 0.3),
                blurRadius: 32,
                offset: const Offset(0, 8),
              ),
            ],
          ),
          child: const Icon(Icons.science_rounded, color: Colors.white, size: 48),
        ),
        const SizedBox(height: 32),

        Text(
          'Paper Trading',
          style: AppTheme.headlineLarge.copyWith(fontSize: 28),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 12),
        Text(
          'Practice trading with ₹2,50,000 of virtual money.\nNo risk. Real experience.',
          style: AppTheme.bodyMedium.copyWith(height: 1.5),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 40),

        // Feature cards
        _buildFeatureCard(
          Icons.timer_rounded,
          '7-Day Challenge',
          'Your simulation runs for exactly 7 days with random, unpredictable market data.',
        ),
        _buildFeatureCard(
          Icons.shuffle_rounded,
          'Truly Random',
          'Prices use a random walk algorithm — no patterns to predict or cheat.',
        ),
        _buildFeatureCard(
          Icons.account_balance_wallet_rounded,
          '₹2,50,000 Virtual Balance',
          'Start with a realistic balance to practice buying and selling.',
        ),
        const SizedBox(height: 32),

        // CTA
        SizedBox(
          width: double.infinity,
          height: 56,
          child: ElevatedButton(
            onPressed: sim.isLoading ? null : () => controller.startSimulation(),
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.primary,
              foregroundColor: Colors.white,
              disabledBackgroundColor: AppTheme.primary.withValues(alpha: 0.5),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
              elevation: 0,
            ),
            child: sim.isLoading
                ? const SizedBox(width: 22, height: 22, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                : const Text(
                    'Start Simulation',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600, fontFamily: AppTheme.fontHeadline),
                  ),
          ),
        ),

        if (sim.error != null)
          Padding(
            padding: const EdgeInsets.only(top: 12),
            child: Text(sim.error!, style: const TextStyle(color: AppTheme.danger, fontSize: 12)),
          ),

        const SizedBox(height: 24),
        Text(
          'You can only run one simulation at a time.',
          style: AppTheme.bodySmall.copyWith(fontSize: 11),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  Widget _buildActiveSimulation(SimulationState sim) {
    return Column(
      children: [
        const SizedBox(height: 16),

        // Status card
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [Color(0xFF1A2636), Color(0xFF141C28)],
            ),
            borderRadius: BorderRadius.circular(AppTheme.radiusLg),
            border: Border.all(color: AppTheme.primary.withValues(alpha: 0.3), width: 0.5),
            boxShadow: [
              BoxShadow(
                color: AppTheme.primary.withValues(alpha: 0.1),
                blurRadius: 32,
                offset: const Offset(0, 12),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(
                      color: AppTheme.success.withValues(alpha: 0.12),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: const Text(
                      'SIMULATION ACTIVE',
                      style: TextStyle(fontSize: 10, fontWeight: FontWeight.w700, letterSpacing: 1, color: AppTheme.success),
                    ),
                  ),
                  const Spacer(),
                  const Icon(Icons.science_rounded, color: AppTheme.primary, size: 20),
                ],
              ),
              const SizedBox(height: 16),
              Text('Virtual Balance', style: AppTheme.bodySmall),
              const SizedBox(height: 4),
              Text(
                '₹${sim.virtualBalance.toStringAsFixed(2)}',
                style: AppTheme.numberLarge.copyWith(fontSize: 32),
              ),
              const SizedBox(height: 16),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppTheme.surfaceVariant.withValues(alpha: 0.3),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.timer_rounded, color: AppTheme.accent, size: 18),
                    const SizedBox(width: 8),
                    Text(
                      sim.remainingTime.isNotEmpty ? '${sim.remainingTime} remaining' : '7 days remaining',
                      style: AppTheme.bodyMedium.copyWith(color: AppTheme.accent, fontWeight: FontWeight.w600),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 24),

        // Instructions
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(20),
          decoration: AppTheme.premiumCard(),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('How It Works', style: AppTheme.headlineSmall.copyWith(fontSize: 15)),
              const SizedBox(height: 12),
              _buildInstructionRow('1', 'Go to Markets to see simulated prices'),
              _buildInstructionRow('2', 'Use Trade to buy/sell with virtual money'),
              _buildInstructionRow('3', 'Track your P&L on the Dashboard'),
              _buildInstructionRow('4', 'Simulation ends after 7 days'),
            ],
          ),
        ),
        const SizedBox(height: 48),
      ],
    );
  }

  Widget _buildFeatureCard(IconData icon, String title, String body) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(18),
      decoration: AppTheme.premiumCard(),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: AppTheme.primary.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, color: AppTheme.primary, size: 22),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(color: AppTheme.textPrimary, fontWeight: FontWeight.w600, fontSize: 14)),
                const SizedBox(height: 3),
                Text(body, style: AppTheme.bodySmall.copyWith(fontSize: 12, height: 1.4)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInstructionRow(String num, String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Row(
        children: [
          Container(
            width: 24,
            height: 24,
            decoration: BoxDecoration(
              color: AppTheme.primary.withValues(alpha: 0.12),
              borderRadius: BorderRadius.circular(6),
            ),
            child: Center(
              child: Text(num, style: TextStyle(color: AppTheme.primary, fontSize: 12, fontWeight: FontWeight.w700)),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(child: Text(text, style: AppTheme.bodyMedium.copyWith(fontSize: 13))),
        ],
      ),
    );
  }
}
