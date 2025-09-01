

from .functions import (_add_collapsible_node, _add_collapsible_node_threaded, _on_collapsed_changed, _on_expanded_changed, _on_main_size_changed, _on_scanning_finished, _populate_expanded_strip, _populate_thumb_tree, _refresh, _renumber_images, _safe_list, _select_index, _show_from_thumb, _show_image, _stop_scanner_thread, load_all_directories_async, next_image, on_folder_selected, on_item_expanded, on_tree_thumb_clicked, open_folder, prev_image, toggle_slideshow, undo_last_renaming)

def initFuncs(self):
    try:
        for f in (_add_collapsible_node, _add_collapsible_node_threaded, _on_collapsed_changed, _on_expanded_changed, _on_main_size_changed, _on_scanning_finished, _populate_expanded_strip, _populate_thumb_tree, _refresh, _renumber_images, _safe_list, _select_index, _show_from_thumb, _show_image, _stop_scanner_thread, load_all_directories_async, next_image, on_folder_selected, on_item_expanded, on_tree_thumb_clicked, open_folder, prev_image, toggle_slideshow, undo_last_renaming):
            setattr(self, f.__name__, f)
    except Exception as e:
        logger.info(f"{e}")
    return self
