import logging
import re

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """
    Post-migración stock_ux 19.0.1.4.0
    Desactiva vistas de módulos desinstalados que no existen en v19.
    Se hace en post-migrate para que corra después de que todos los
    módulos carguen y antes de que el servidor levante.
    """
    _logger.info("stock_ux post-migrate: desactivando vistas de módulos desinstalados")

    vistas = [
        # stock_voucher
        ('stock_voucher', 'view_move_tree'),
        ('stock_voucher', 'view_picking_form'),
        ('stock_voucher', 'view_picking_type_form'),
        ('stock_voucher', 'view_print_stock_voucher_form'),
        ('stock_voucher', 'view_stock_picking_voucher_form'),
        ('stock_voucher', 'view_stock_picking_voucher_tree'),
        ('stock_voucher', 'vpicktree'),
        # stock_reserve
        ('stock_reserve', 'product_product_form_view_reservation_button'),
        ('stock_reserve', 'product_template_form_view_reservation_button'),
        # stock_batch_picking_ux
        ('stock_batch_picking_ux', 'custom_label_transfer_template_view_pdf'),
        ('stock_batch_picking_ux', 'custom_label_transfer_template_view_zpl'),
        ('stock_batch_picking_ux', 'vpicktree'),
        # stock_picking_purchase_order_link
        ('stock_picking_purchase_order_link', 'view_picking_form'),
        # stock_picking_sale_order_link
        ('stock_picking_sale_order_link', 'view_picking_form'),
        # stock_picking_show_return
        ('stock_picking_show_return', 'view_picking_form'),
        # purchase_stock_ux
        ('purchase_stock_ux', 'purchase_order_line_search'),
        ('purchase_stock_ux', 'purchase_order_line_tree'),
        # sale_stock_picking_note
        ('sale_stock_picking_note', 'view_picking_form'),
        ('sale_stock_picking_note', 'view_order_form'),
        ('sale_stock_picking_note', 'view_partner_form_inherit_partner_picking_note'),
        ('sale_stock_picking_note', 'report_delivery_document_customer_note'),
        # l10n_ar_withholding_ux
        ('l10n_ar_withholding_ux', 'report_payment_receipt_document'),
        # account_tax_settlement
        ('account_tax_settlement', 'view_account_tax_settlement_wizard_form'),
        ('account_tax_settlement', 'view_download_files_wizard_search'),
        ('account_tax_settlement', 'download_files_wizard'),
        ('account_tax_settlement', 'view_account_move_line_filter'),
        ('account_tax_settlement', 'view_account_move_line_tree'),
        ('account_tax_settlement', 'view_move_form'),
        ('account_tax_settlement', 'view_account_journal_form'),
        ('account_tax_settlement', 'account_report_form'),
        # l10n_ar_account_tax_settlement
        ('l10n_ar_account_tax_settlement', 'inflation_adjustment_form'),
        ('l10n_ar_account_tax_settlement', 'inflation_adjustment_index_tree'),
        ('l10n_ar_account_tax_settlement', 'inflation_adjustment_index_search'),
        ('l10n_ar_account_tax_settlement', 'view_tax_form_inherited'),
        # l10n_ar_account_withholding
        ('l10n_ar_account_withholding', 'view_res_company_jurisdiction_padron_tree'),
        ('l10n_ar_account_withholding', 'view_res_company_jurisdiction_padron_form'),
        ('l10n_ar_account_withholding', 'view_partner_form'),
        ('l10n_ar_account_withholding', 'res_config_settings_view_form'),
        ('l10n_ar_account_withholding', 'view_afip_tabla_ganancias_escala_tree'),
        ('l10n_ar_account_withholding', 'view_afip_tabla_ganancias_alicuotasymontos_tree'),
        ('l10n_ar_account_withholding', 'view_account_payment_tree'),
        ('l10n_ar_account_withholding', 'view_res_partner_arba_alicuot_tree'),
        ('l10n_ar_account_withholding', 'view_res_partner_arba_alicuot_form'),
        ('l10n_ar_account_withholding', 'view_partner_withholding_amount_type_form'),
        # l10n_ar_withholding_ux
        ('l10n_ar_withholding_ux', 'view_tax_form'),
        ('l10n_ar_withholding_ux', 'view_l10n_ar_payment_withholding_form'),
        ('l10n_ar_withholding_ux', 'view_account_tax_search'),
        ('l10n_ar_withholding_ux', 'report_withholding_certificate_document'),
        ('l10n_ar_withholding_ux', 'report_withholding_certificate'),
        ('l10n_ar_withholding_ux', 'report_payment_receipt'),
        # stock_account_ux
        ('stock_account_ux', 'view_move_form'),
        # l10n_ar_stock_adhoc
        ('l10n_ar_stock_adhoc', 'product_template_form_view'),
        ('l10n_ar_stock_adhoc', 'product_uom_tree_view'),
        ('l10n_ar_stock_adhoc', 'report_deliveryslip'),
        ('l10n_ar_stock_adhoc', 'report_invoice_document'),
        ('l10n_ar_stock_adhoc', 'res_config_settings_view_form'),
        ('l10n_ar_stock_adhoc', 'search_product_lot_filter'),
        ('l10n_ar_stock_adhoc', 'view_arba_cot_wizard'),
        ('l10n_ar_stock_adhoc', 'view_picking_cot_form'),
        ('l10n_ar_stock_adhoc', 'view_production_lot_form'),
        ('l10n_ar_stock_adhoc', 'view_production_lot_tree'),
        ('l10n_ar_stock_adhoc', 'view_stock_book_form'),
        # stock_voucher - vistas adicionales
        ('stock_voucher', 'view_stock_book_tree'),
        ('stock_voucher', 'view_stock_book_form'),
        ('stock_voucher', 'view_picking_internal_search'),
        ('stock_voucher', 'view_move_search'),
        ('stock_voucher', 'custom_label_transfer_template_view_zpl'),
        ('stock_voucher', 'custom_label_transfer_template_view_pdf'),
        ('stock_voucher', 'custom_barcode_transfer_template_view_zpl'),
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
            _logger.info(f"  ✓ {module}.{xmlid} desactivada")
            total += 1

    _logger.info(f"stock_ux post-migrate: {total} vistas desactivadas")

    # Desactivar acciones con modelos inexistentes
    _logger.info("stock_ux post-migrate: desactivando acciones con modelos inexistentes")
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
    _logger.info(f"  ✓ {cr.rowcount} acciones con modelos inexistentes desactivadas")

    cr.execute("""
        UPDATE ir_act_window
        SET binding_model_id = NULL
        WHERE domain::text LIKE '%tax_settlement%'
    """)
    _logger.info(f"  ✓ {cr.rowcount} acciones con dominio tax_settlement desactivadas")

    # Desactivar menús que apuntan a modelos inexistentes
    _logger.info("stock_ux post-migrate: desactivando menús con modelos inexistentes")
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
    _logger.info(f"  ✓ {cr.rowcount} menús desactivados")

    # Desactivar vistas de enseco_report_custom (módulo desinstalado)
    # El nuevo módulo las va a recrear al instalarse
    _logger.info("stock_ux post-migrate: desactivando vistas de enseco_report_custom")
    cr.execute("""
        UPDATE ir_ui_view SET active = False
        WHERE id IN (
            SELECT res_id FROM ir_model_data
            WHERE module = 'enseco_report_custom'
            AND model = 'ir.ui.view'
        )
        AND active = True
    """)
    _logger.info(f"  ✓ {cr.rowcount} vistas de enseco_report_custom desactivadas")

    # Desactivar acción del reporte stock_voucher
    _logger.info("stock_ux post-migrate: desactivando acción reporte stock_voucher")
    cr.execute("""
        UPDATE ir_act_report_xml SET binding_model_id = NULL
        WHERE report_name LIKE '%stock_voucher%'
    """)
    _logger.info(f"  ✓ {cr.rowcount} acciones de reporte stock_voucher desactivadas")

    # Corregir templates de Studio con campos obsoletos en v19
    _logger.info("stock_ux post-migrate: corrigiendo templates de Studio con campos obsoletos")

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
        _logger.info("  ✓ Template Studio sale (4152): product_uom → product_uom_id")

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
        _logger.info("  ✓ Template Studio delivery (4161): product_packaging_id eliminado")