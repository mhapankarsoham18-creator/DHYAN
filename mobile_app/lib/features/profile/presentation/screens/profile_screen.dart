import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile_app/core/theme/app_theme.dart';
import 'package:mobile_app/core/providers/app_settings_provider.dart';
import 'package:mobile_app/core/network/dio_client.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:go_router/go_router.dart';

class ProfileScreen extends ConsumerStatefulWidget {
  const ProfileScreen({super.key});

  @override
  ConsumerState<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends ConsumerState<ProfileScreen> {
  final _nameController = TextEditingController(text: 'Dhyan User');
  final _phoneController = TextEditingController(text: '+91 90291 62302');
  bool _isEditing = false;
  bool _isSaving = false;
  List<String> _connectedBrokers = [];
  double _virtualBalance = 0.0;

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  Future<void> _loadProfile() async {
    try {
      final resp = await dioClient.dio.get('/api/v1/auth/me');
      final data = resp.data;
      setState(() {
        _nameController.text = data['name'] ?? 'User';
        _phoneController.text = data['phone_number'] ?? '';
        
        final brokers = data['connected_brokers'];
        if (brokers != null && brokers is List) {
          _connectedBrokers = brokers.map((e) => e.toString()).toList();
        }
        
        _virtualBalance = (data['virtual_balance'] ?? 0.0).toDouble();
      });
    } catch (_) {}
  }

  Future<void> _saveProfile() async {
    setState(() => _isSaving = true);
    try {
      await dioClient.dio.patch('/api/v1/auth/profile', data: {
        'name': _nameController.text.trim(),
      });
      setState(() { _isEditing = false; _isSaving = false; });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Profile updated')),
        );
      }
    } catch (e) {
      setState(() => _isSaving = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to save: $e')),
        );
      }
    }
  }

  @override
  void dispose() {
    _nameController.dispose();
    _phoneController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final settings = ref.watch(appSettingsProvider);
    final settingsNotifier = ref.read(appSettingsProvider.notifier);

    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        leading: IconButton(
          onPressed: () => Scaffold.of(context).openDrawer(),
          icon: const Icon(Icons.menu_rounded, size: 22),
        ),
        title: const Text('Profile'),
        actions: [
          if (_isEditing)
            TextButton(
              onPressed: _isSaving ? null : _saveProfile,
              child: _isSaving
                  ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: AppTheme.primary))
                  : Text('Save', style: TextStyle(color: AppTheme.primary, fontWeight: FontWeight.w600)),
            )
          else
            IconButton(
              onPressed: () => setState(() => _isEditing = true),
              icon: const Icon(Icons.edit_rounded, color: AppTheme.primary, size: 20),
            ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        physics: const BouncingScrollPhysics(),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
          // ── Avatar & Name ──────────────────────
          _buildAvatarSection(),
          const SizedBox(height: 32),

          // ── Account Info ───────────────────────
          _buildSectionHeader('ACCOUNT'),
          _buildInfoTile(Icons.phone_rounded, 'Phone', _phoneController.text),
          _buildProfileOption(
            Icons.account_balance_outlined,
            'Connected Brokers',
            _connectedBrokers.isEmpty ? 'None' : _connectedBrokers.join(', '),
          ),
          _buildProfileOption(
            Icons.account_balance_wallet_outlined,
            'Funds',
            'Available: ₹${_virtualBalance.toStringAsFixed(2)}',
          ),
          const SizedBox(height: 24),

          // ── Trading Tools ──────────────────────
          _buildSectionHeader('TRADING TOOLS'),
          _buildProfileOption(
            Icons.history_edu_outlined,
            'Trading Journal',
            '12 entries this month',
          ),
          _buildProfileOption(
            Icons.analytics_outlined,
            'Weekly Reports',
            'Last report: March 24',
          ),
          _buildProfileOption(
            Icons.calculate_outlined,
            'Tax P&L',
            'FY 2025-26',
          ),
          const SizedBox(height: 24),

          // ── Preferences ────────────────────────
          _buildSectionHeader('PREFERENCES'),
          _buildToggleOption(
            Icons.bolt_outlined,
            'Simple Mode',
            settings.isSimpleMode,
            (_) => settingsNotifier.toggleSimpleMode(),
          ),
          const SizedBox(height: 40),

          // ── Logout ─────────────────────────────
          _buildLogoutButton(),
          const SizedBox(height: 16),
          Center(
            child: Text(
              'Dhyan v1.0.0 — Built for mindful trading',
              style: AppTheme.bodySmall.copyWith(fontSize: 11),
            ),
          ),
          const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  Widget _buildAvatarSection() {
    return Center(
      child: Column(
        children: [
          // Avatar with glow
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: AppTheme.primaryGradient,
              boxShadow: [
                BoxShadow(
                  color: AppTheme.primary.withValues(alpha: 0.3),
                  blurRadius: 24,
                  offset: const Offset(0, 8),
                ),
              ],
            ),
            child: Center(
              child: Text(
                _nameController.text.isNotEmpty ? _nameController.text[0].toUpperCase() : 'D',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 32,
                  fontWeight: FontWeight.w700,
                  fontFamily: AppTheme.fontHeadline,
                ),
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Editable name
          if (_isEditing)
            SizedBox(
              width: 200,
              child: TextField(
                controller: _nameController,
                textAlign: TextAlign.center,
                style: AppTheme.headlineMedium.copyWith(fontSize: 20),
                decoration: InputDecoration(
                  hintText: 'Your name',
                  hintStyle: TextStyle(color: AppTheme.textTertiary),
                  border: UnderlineInputBorder(
                    borderSide: BorderSide(color: AppTheme.primary.withValues(alpha: 0.5)),
                  ),
                  focusedBorder: const UnderlineInputBorder(
                    borderSide: BorderSide(color: AppTheme.primary),
                  ),
                ),
              ),
            )
          else
            Text(
              _nameController.text,
              style: AppTheme.headlineMedium.copyWith(fontSize: 20),
            ),
          const SizedBox(height: 4),
          Text(
            _phoneController.text,
            style: AppTheme.bodyMedium.copyWith(fontSize: 13),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12, left: 4),
      child: Text(
        title,
        style: AppTheme.labelMedium.copyWith(
          fontSize: 11,
          letterSpacing: 1.5,
          color: AppTheme.primary,
        ),
      ),
    );
  }

  Widget _buildInfoTile(IconData icon, String label, String value) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      decoration: AppTheme.premiumCard(),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: AppTheme.primary.withValues(alpha: 0.08),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(icon, color: AppTheme.textSecondary, size: 20),
          ),
          const SizedBox(width: 14),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(label, style: AppTheme.bodySmall.copyWith(fontSize: 11)),
              Text(value, style: const TextStyle(color: AppTheme.textPrimary, fontWeight: FontWeight.w500, fontSize: 14)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildProfileOption(IconData icon, String title, String subtitle, {VoidCallback? onTap}) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.only(bottom: 8),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        decoration: AppTheme.premiumCard(),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: AppTheme.primary.withValues(alpha: 0.08),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(icon, color: AppTheme.textSecondary, size: 20),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: const TextStyle(color: AppTheme.textPrimary, fontWeight: FontWeight.w500, fontSize: 14)),
                  Text(subtitle, style: AppTheme.bodySmall.copyWith(fontSize: 11)),
                ],
              ),
            ),
            const Icon(Icons.chevron_right_rounded, color: AppTheme.textTertiary, size: 18),
          ],
        ),
      ),
    );
  }

  Widget _buildToggleOption(IconData icon, String title, bool value, ValueChanged<bool> onChanged) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: AppTheme.premiumCard(),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: AppTheme.primary.withValues(alpha: 0.08),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(icon, color: AppTheme.textSecondary, size: 20),
          ),
          const SizedBox(width: 14),
          Expanded(child: Text(title, style: const TextStyle(color: AppTheme.textPrimary, fontWeight: FontWeight.w500, fontSize: 14))),
          Switch(value: value, onChanged: onChanged),
        ],
      ),
    );
  }

  Widget _buildLogoutButton() {
    return SizedBox(
      width: double.infinity,
      height: 52,
      child: OutlinedButton.icon(
        onPressed: () async {
          const storage = FlutterSecureStorage();
          await storage.delete(key: 'jwt_token');
          if (mounted) context.go('/login');
        },
        icon: const Icon(Icons.logout_rounded, size: 18),
        label: const Text('Logout', style: TextStyle(fontWeight: FontWeight.w600)),
        style: OutlinedButton.styleFrom(
          foregroundColor: AppTheme.danger,
          side: BorderSide(color: AppTheme.danger.withValues(alpha: 0.5)),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        ),
      ),
    );
  }
}
