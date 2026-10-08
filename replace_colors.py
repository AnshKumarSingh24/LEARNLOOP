import os, re

color_map = {
    r'Colors\.white\.withValues\(': 'LibraryDesignSystem.textPrimary.withValues(',
    r'Colors\.white24': 'LibraryDesignSystem.textPrimary.withValues(alpha: 0.24)',
    r'Colors\.white30': 'LibraryDesignSystem.textPrimary.withValues(alpha: 0.30)',
    r'Colors\.white38': 'LibraryDesignSystem.textPrimary.withValues(alpha: 0.38)',
    r'Colors\.white54': 'LibraryDesignSystem.textPrimary.withValues(alpha: 0.54)',
    r'Colors\.white60': 'LibraryDesignSystem.textPrimary.withValues(alpha: 0.60)',
    r'Colors\.white70': 'LibraryDesignSystem.textPrimary.withValues(alpha: 0.70)',
    r'Colors\.white': 'LibraryDesignSystem.textPrimary',
    r'Colors\.black87': 'LibraryDesignSystem.textPrimary',
    r'Colors\.black54': 'LibraryDesignSystem.textSecondary',
    r'Colors\.black38': 'LibraryDesignSystem.textMuted',
    r'Colors\.black26': 'LibraryDesignSystem.borderDark',
    r'Colors\.black12': 'LibraryDesignSystem.borderDark',
    r'Colors\.black': 'LibraryDesignSystem.textPrimary',
    r'Colors\.grey\.shade50': 'LibraryDesignSystem.surface',
    r'Colors\.grey\.shade100': 'LibraryDesignSystem.surface',
    r'Colors\.grey\.shade200': 'LibraryDesignSystem.borderDark',
    r'Colors\.grey\.shade300': 'LibraryDesignSystem.borderDark',
    r'Colors\.grey\.shade400': 'LibraryDesignSystem.textMuted',
    r'Colors\.grey\.shade500': 'LibraryDesignSystem.textSecondary',
    r'Colors\.grey\.shade600': 'LibraryDesignSystem.textSecondary',
    r'Colors\.grey\.shade700': 'LibraryDesignSystem.textPrimary',
    r'Colors\.grey\.shade800': 'LibraryDesignSystem.textPrimary',
    r'Colors\.grey\.shade900': 'LibraryDesignSystem.textPrimary',
    r'Colors\.grey': 'LibraryDesignSystem.textSecondary'
}

lib_dir = 'capture_app/lib'
for root, dirs, files in os.walk(lib_dir):
    for file in files:
        if file.endswith('.dart'):
            filepath = os.path.join(root, file)
            if 'custom_bottom_nav' in filepath or 'library_design_system' in filepath or 'app_theme' in filepath or 'app_colors' in filepath:
                continue
                
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original = content
            needs_import = False
            for k, v in color_map.items():
                if re.search(k, content):
                    content = re.sub(k, v, content)
                    needs_import = True
            
            if needs_import and 'LibraryDesignSystem' not in original and 'import' in content:
                import_stmt = "import 'package:capture_app/config/library_design_system.dart';"
                if 'library_design_system.dart' not in content:
                    lines = content.splitlines()
                    for i, line in enumerate(lines):
                        if line.startswith('import'):
                            lines.insert(i, import_stmt)
                            break
                    content = '\n'.join(lines)
            
            if content != original:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
print("Done")
