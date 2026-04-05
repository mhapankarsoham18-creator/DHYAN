import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile_app/core/theme/app_theme.dart';
import 'package:mobile_app/features/dashboard/presentation/screens/dashboard_screen.dart';
import 'package:mobile_app/features/markets/presentation/screens/markets_screen.dart';
import 'package:mobile_app/features/trade/presentation/screens/trade_screen.dart';
import 'package:mobile_app/features/alerts/presentation/screens/alerts_screen.dart';
import 'package:mobile_app/features/profile/presentation/screens/profile_screen.dart';
import 'package:mobile_app/features/settings/presentation/screens/settings_screen.dart';
import 'package:mobile_app/features/notifications/presentation/screens/notifications_screen.dart';
import 'package:mobile_app/features/simulation/presentation/screens/simulation_screen.dart';

class MainNavigationScreen extends ConsumerStatefulWidget {
  const MainNavigationScreen({super.key});

  @override
  ConsumerState<MainNavigationScreen> createState() => _MainNavigationScreenState();
}

class _MainNavigationScreenState extends ConsumerState<MainNavigationScreen> {
  int _selectedIndex = 0;
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();

  final List<Widget> _screens = [
    const DashboardScreen(),
    const MarketsScreen(),
    const TradeScreen(),
    const AlertsScreen(),
    const SimulationScreen(),
    const ProfileScreen(),
    const SettingsScreen(),
    const NotificationsScreen(),
  ];

  final List<_NavItem> _navItems = const [
    _NavItem(Icons.dashboard_rounded, Icons.dashboard_outlined, 'Dashboard'),
    _NavItem(Icons.candlestick_chart_rounded, Icons.candlestick_chart_outlined, 'Markets'),
    _NavItem(Icons.swap_horiz_rounded, Icons.swap_horiz_outlined, 'Trade'),
    _NavItem(Icons.notifications_active_rounded, Icons.notifications_none_outlined, 'Alerts'),
    _NavItem(Icons.science_rounded, Icons.science_outlined, 'Simulation'),
    _NavItem(Icons.person_rounded, Icons.person_outline_rounded, 'Profile'),
    _NavItem(Icons.settings_rounded, Icons.settings_outlined, 'Settings'),
    _NavItem(Icons.inbox_rounded, Icons.inbox_outlined, 'Notifications'),
  ];

  void _onItemTapped(int index) {
    setState(() => _selectedIndex = index);
    Navigator.of(context).pop(); // Close drawer
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      key: _scaffoldKey,
      body: IndexedStack(
        index: _selectedIndex,
        children: _screens,
      ),
      drawer: _buildPremiumDrawer(),
    );
  }

  Widget _buildPremiumDrawer() {
    return Drawer(
      width: 280,
      backgroundColor: AppTheme.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.horizontal(right: Radius.circular(0)),
      ),
      child: Column(
        children: [
          // ── User Header ──────────────────────────────────
          _buildDrawerHeader(),
          
          const SizedBox(height: 8),

          // ── Navigation Items ─────────────────────────────
          Expanded(
            child: ListView(
              padding: const EdgeInsets.symmetric(horizontal: 12),
              physics: const BouncingScrollPhysics(),
              children: [
                _buildNavSection('MAIN', [0, 1, 2]),
                const SizedBox(height: 16),
                _buildNavSection('TOOLS', [3, 4]),
                const SizedBox(height: 16),
                _buildNavSection('ACCOUNT', [5, 6, 7]),
              ],
            ),
          ),

          // ── Footer ───────────────────────────────────────
          _buildDrawerFooter(),
        ],
      ),
    );
  }

  Widget _buildDrawerHeader() {
    return Container(
      width: double.infinity,
      padding: EdgeInsets.fromLTRB(20, MediaQuery.of(context).padding.top + 24, 20, 20),
      decoration: const BoxDecoration(
        gradient: AppTheme.cardGradient,
        border: Border(bottom: BorderSide(color: AppTheme.surfaceVariant, width: 0.5)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Avatar
          Container(
            width: 52,
            height: 52,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: AppTheme.primaryGradient,
              boxShadow: [
                BoxShadow(
                  color: AppTheme.primary.withValues(alpha: 0.4),
                  blurRadius: 16,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: const Center(
              child: Text(
                'D',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 22,
                  fontWeight: FontWeight.w700,
                  fontFamily: AppTheme.fontHeadline,
                ),
              ),
            ),
          ),
          const SizedBox(height: 14),
          const Text(
            'Dhyan User',
            style: TextStyle(
              color: AppTheme.textPrimary,
              fontSize: 17,
              fontWeight: FontWeight.w600,
              fontFamily: AppTheme.fontHeadline,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            '+91 •••• •••• ••',
            style: TextStyle(
              color: AppTheme.textSecondary.withValues(alpha: 0.7),
              fontSize: 13,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildNavSection(String title, List<int> indices) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          child: Text(
            title,
            style: AppTheme.labelMedium.copyWith(
              fontSize: 10,
              letterSpacing: 1.5,
              color: AppTheme.textTertiary,
            ),
          ),
        ),
        ...indices.map((i) => _buildNavTile(i)),
      ],
    );
  }

  Widget _buildNavTile(int index) {
    final item = _navItems[index];
    final isSelected = _selectedIndex == index;

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Material(
        color: Colors.transparent,
        borderRadius: BorderRadius.circular(AppTheme.radiusMd),
        child: InkWell(
          onTap: () => _onItemTapped(index),
          borderRadius: BorderRadius.circular(AppTheme.radiusMd),
          splashColor: AppTheme.primary.withValues(alpha: 0.1),
          highlightColor: AppTheme.primary.withValues(alpha: 0.05),
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            curve: Curves.easeOutCubic,
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
            decoration: BoxDecoration(
              color: isSelected
                  ? AppTheme.primary.withValues(alpha: 0.12)
                  : Colors.transparent,
              borderRadius: BorderRadius.circular(AppTheme.radiusMd),
            ),
            child: Row(
              children: [
                Icon(
                  isSelected ? item.activeIcon : item.icon,
                  color: isSelected ? AppTheme.primary : AppTheme.textSecondary,
                  size: 20,
                ),
                const SizedBox(width: 14),
                Text(
                  item.label,
                  style: TextStyle(
                    color: isSelected ? AppTheme.primaryLight : AppTheme.textSecondary,
                    fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
                    fontSize: 14,
                  ),
                ),
                if (index == 4) ...[
                  const Spacer(),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: AppTheme.accent.withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: const Text(
                      'NEW',
                      style: TextStyle(
                        color: AppTheme.accent,
                        fontSize: 9,
                        fontWeight: FontWeight.w700,
                        letterSpacing: 0.5,
                      ),
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildDrawerFooter() {
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 12, 20, 20),
      decoration: const BoxDecoration(
        border: Border(top: BorderSide(color: AppTheme.surfaceVariant, width: 0.5)),
      ),
      child: Column(
        children: [
          Text(
            'Dhyan v1.0.0',
            style: AppTheme.bodySmall.copyWith(fontSize: 11),
          ),
          const SizedBox(height: 2),
          Text(
            'Built for mindful trading',
            style: AppTheme.bodySmall.copyWith(fontSize: 10, color: AppTheme.textTertiary),
          ),
        ],
      ),
    );
  }
}

class _NavItem {
  final IconData activeIcon;
  final IconData icon;
  final String label;

  const _NavItem(this.activeIcon, this.icon, this.label);
}
