import logging
import re

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """
    Post-migración stock_ux 19.0.1.5.0
    Orquestador principal de limpieza y reactivación de vistas post-upgrade.

    Estrategia:
    1. Desactivar TODAS las vistas de módulos completamente desinstalados
    2. Desactivar vistas específicas con campos obsoletos (other_currency)
    3. Reactivar vistas críticas para el negocio (reportes AR, stock)
    4. Desactivar vistas específicas problemáticas (legacy)
    5. Limpiar acciones, menús y templates obsoletos
    """

    _logger.info("=" * 70)
    _logger.info("stock_ux post-migrate 19.0.1.5.0: limpieza y reactivación")
    _logger.info("=" * 70)

    # ==================================================================
    # 1. Desactivar módulos completamente desinstalados
    # ==================================================================
    modulos_desinstalados_completos = [
        'stock_voucher',
        'stock_reserve',
        'stock_batch_picking_ux',
        'stock_picking_purchase_order_link',
        'stock_picking_sale_order_link',
        'stock_picking_show_return',
        'account_tax_settlement',
        'l10n_ar_account_tax_settlement',
        'l10n_ar_account_withholding',
        'stock_account_ux',
        'l10n_ar_stock_adhoc',
        #'purchase_ux',  # <-- NUEVO: desactivar completamente purchase_ux
        # 'enseco_report_custom',  # Ahora está instalado en v19, no desactivar sus vistas
    ]

    _logger.info("1. Desactivando TODAS las vistas de módulos desinstalados")
    cr.execute("""
        UPDATE ir_ui_view SET active = False
        WHERE id IN (
            SELECT res_id FROM ir_model_data
            WHERE module = ANY(%s)
            AND model = 'ir.ui.view'
        )
        AND active = True
    """, (modulos_desinstalados_completos,))
    _logger.info(f"   ✓ {cr.rowcount} vistas de módulos desinstalados desactivadas")

    # ==================================================================
    # 2. Desactivar vistas específicas con campos obsoletos (other_currency)
    # ==================================================================
    _logger.info("2. Desactivando vistas con campos obsoletos (other_currency)")
    cr.execute("""
        UPDATE ir_ui_view SET active = False
        WHERE id IN (3974, 4263, 4594) AND active = True
    """)
    _logger.info(f"   ✓ {cr.rowcount} vistas con other_currency desactivadas")

    # ==================================================================
    # 3. Reactivar vistas críticas para el negocio
    # ==================================================================
    _logger.info("3. Reactivando vistas críticas (reportes AR, stock)")

    vistas_a_reactivar = [
        ('l10n_ar_sale', 'report_saleorder_document'),
        ('sale_ux', 'report_saleorder'),
        ('stock_ux', 'view_picking_form'),
        ('stock_ux', 'view_move_line_tree'),
    ]

    reactivadas = 0
    for module, xmlid in vistas_a_reactivar:
        cr.execute("""
            UPDATE ir_ui_view v
            SET active = True
            FROM ir_model_data d
            WHERE d.res_id = v.id
              AND d.model = 'ir.ui.view'
              AND d.module = %s
              AND d.name = %s
              AND v.active = False
        """, (module, xmlid))
        if cr.rowcount > 0:
            _logger.info(f"   ✓ {module}.{xmlid} reactivada")
            reactivadas += 1
        else:
            _logger.info(f"   - {module}.{xmlid} ya estaba activa")

    _logger.info(f"   Total vistas reactivadas: {reactivadas}")

    # ==================================================================
    # 4. Desactivar vistas específicas de módulos instalados (legacy)
    # ==================================================================
    _logger.info("4. Desactivando vistas específicas problemáticas (legacy)")
    vistas = [
        # purchase_stock_ux (instalado pero vistas con campos obsoletos)
        ('purchase_stock_ux', 'purchase_order_line_search'),
        ('purchase_stock_ux', 'purchase_order_line_tree'),
        # sale_stock_picking_note (instalado pero campo picking_note eliminado)
        ('sale_stock_picking_note', 'view_picking_form'),
        ('sale_stock_picking_note', 'view_order_form'),
        ('sale_stock_picking_note', 'view_partner_form_inherit_partner_picking_note'),
        ('sale_stock_picking_note', 'report_delivery_document_customer_note'),
        # l10n_ar_withholding_ux (instalado pero vistas con campos obsoletos)
        ('l10n_ar_withholding_ux', 'report_payment_receipt_document'),
        ('l10n_ar_withholding_ux', 'view_tax_form'),
        ('l10n_ar_withholding_ux', 'view_l10n_ar_payment_withholding_form'),
        ('l10n_ar_withholding_ux', 'view_account_tax_search'),
        ('l10n_ar_withholding_ux', 'report_withholding_certificate_document'),
        ('l10n_ar_withholding_ux', 'report_withholding_certificate'),
        ('l10n_ar_withholding_ux', 'report_payment_receipt'),
        # studio_customization - vista hija con product_uom obsoleto
        ('studio_customization', 'web_studio_report_ed_06cda52f-63b6-4712-bced-8de16bbe3c81'),
    ]

    total = 0
    for module, xmlid in vistas:
        cr.execute("""
            UPDATE ir_ui_view v
            SET active = False
            FROM ir_model_data d
            WHERE d.res_id = v.id
              AND d.model = 'ir.ui.view'
              AND d.module = %s
              AND d.name = %s
              AND v.active = True
        """, (module, xmlid))
        if cr.rowcount > 0:
            _logger.info(f"   ✓ {module}.{xmlid} desactivada")
            total += 1

    _logger.info(f"   Total vistas legacy desactivadas: {total}")

    # ==================================================================
    # 5. Desactivar acciones con modelos inexistentes
    # ==================================================================
    _logger.info("5. Desactivando acciones con modelos inexistentes")
    cr.execute("""
        UPDATE ir_act_window
        SET binding_model_id = NULL
        WHERE res_model IN (
            'afip.tabla_ganancias.escala',
            'afip.tabla_ganancias.alicuotasymontos',
            'stock.book',
            'stock.reservation'
        )
    """)
    _logger.info(f"   ✓ {cr.rowcount} acciones con modelos inexistentes desactivadas")

    cr.execute("""
        UPDATE ir_act_window
        SET binding_model_id = NULL
        WHERE domain::text LIKE '%tax_settlement%'
    """)
    _logger.info(f"   ✓ {cr.rowcount} acciones con dominio tax_settlement desactivadas")

    # ==================================================================
    # 6. Desactivar menús que apuntan a modelos inexistentes
    # ==================================================================
    _logger.info("6. Desactivando menús con modelos inexistentes")
    cr.execute("""
        UPDATE ir_ui_menu SET active = False
        WHERE action IN (
            SELECT 'ir.actions.act_window,' || id::text
            FROM ir_act_window
            WHERE res_model IN (
                'afip.tabla_ganancias.escala',
                'afip.tabla_ganancias.alicuotasymontos',
                'stock.book',
                'stock.reservation'
            )
            OR domain::text LIKE '%tax_settlement%'
        )
    """)
    _logger.info(f"   ✓ {cr.rowcount} menús desactivados")

    # ==================================================================
    # 7. Desactivar acción del reporte stock_voucher
    # ==================================================================
    _logger.info("7. Desactivando acción reporte stock_voucher")
    cr.execute("""
        UPDATE ir_act_report_xml SET binding_model_id = NULL
        WHERE report_name LIKE '%stock_voucher%'
    """)
    _logger.info(f"   ✓ {cr.rowcount} acciones de reporte stock_voucher desactivadas")

    # ==================================================================
    # 8. Corregir templates de Studio con campos obsoletos en v19
    # ==================================================================
    _logger.info("8. Corrigiendo templates de Studio con campos obsoletos")

    # 4152: sale report copy - product_uom renombrado a product_uom_id en v19
    cr.execute("""
        UPDATE ir_ui_view
        SET arch_db = CAST(
            regexp_replace(
                arch_db::text,
                't-field="line\\.product_uom"',
                't-field="line.product_uom_id"',
                'g'
            ) AS jsonb
        )
        WHERE id = 4152
        AND arch_db::text LIKE '%line.product_uom%'
    """)
    if cr.rowcount > 0:
        _logger.info("   ✓ Template Studio sale (4152): product_uom → product_uom_id")

    # 4161: delivery report copy - product_packaging_id no existe en stock.move en v19
    cr.execute("""
        UPDATE ir_ui_view
        SET arch_db = CAST(
            regexp_replace(
                arch_db::text,
                '<span[^>]*t-if="move\\.product_packaging_id"[^/]*/?>',
                '',
                'g'
            ) AS jsonb
        )
        WHERE id = 4161
        AND arch_db::text LIKE '%product_packaging_id%'
    """)
    if cr.rowcount > 0:
        _logger.info("   ✓ Template Studio delivery (4161): product_packaging_id eliminado")

    # ==================================================================
    # Resumen final
    # ==================================================================
    _logger.info("=" * 70)
    _logger.info("stock_ux post-migrate 19.0.1.5.0: completado")
    _logger.info("=" * 70)