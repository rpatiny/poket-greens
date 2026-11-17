extends Node2D
## Cena principal: mundo (mapa + jogador), câmera e interface (diálogo, transição, nome do lugar).

const START_MAP := "garagem"
const FADE_TIME := 0.18

var current_map: GameMap
var player: Player
var camera: Camera2D
var dialog: DialogBox

var _world: Node2D
var _fade: ColorRect
var _banner: PanelContainer
var _banner_label: Label
var _transitioning := false
var _banner_tween: Tween


func _enter_tree() -> void:
	Game.main = self


func _ready() -> void:
	_world = Node2D.new()
	_world.name = "World"
	add_child(_world)

	camera = Camera2D.new()
	camera.name = "Camera"
	add_child(camera)
	camera.make_current()

	var ui := CanvasLayer.new()
	ui.name = "UI"
	add_child(ui)
	dialog = DialogBox.new()
	ui.add_child(dialog)
	_build_banner(ui)
	_fade = ColorRect.new()
	_fade.name = "Fade"
	_fade.color = Color("#1d1922")
	_fade.set_anchors_preset(Control.PRESET_FULL_RECT)
	_fade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ui.add_child(_fade)

	player = Player.new()
	player.name = "Player"

	var start: Dictionary = Game.map_data(START_MAP).get("spawn", {})
	var c: Array = start.get("cell", [1, 1])
	_load_map(START_MAP, Vector2i(int(c[0]), int(c[1])), Game.DIRS[start.get("facing", "down")])
	var tw := create_tween()
	tw.tween_property(_fade, "modulate:a", 0.0, 0.5)


func _process(_delta: float) -> void:
	_update_camera()


func is_busy() -> bool:
	return _transitioning or dialog.open


func say(lines: Array, speaker := "") -> void:
	if lines.is_empty():
		return
	dialog.show_lines(lines, speaker)
	await dialog.finished


func change_map(map_id: String, cell: Vector2i, facing: Vector2i) -> void:
	_transitioning = true
	var tw := create_tween()
	tw.tween_property(_fade, "modulate:a", 1.0, FADE_TIME)
	await tw.finished
	_load_map(map_id, cell, facing)
	tw = create_tween()
	tw.tween_property(_fade, "modulate:a", 0.0, FADE_TIME)
	await tw.finished
	_transitioning = false


func _load_map(map_id: String, cell: Vector2i, facing: Vector2i) -> void:
	if player.get_parent():
		player.get_parent().remove_child(player)
	if current_map:
		current_map.queue_free()
		_world.remove_child(current_map)
	current_map = GameMap.new()
	current_map.setup(map_id)
	_world.add_child(current_map)
	current_map.add_entity(player)
	player.place(cell, facing)
	_update_camera()
	_show_banner(tr(current_map.data.get("name", map_id)))


## Segue o jogador; se o mapa for menor que a tela, centraliza (interiores com fundo escuro).
func _update_camera() -> void:
	if current_map == null:
		return
	var view := get_viewport_rect().size
	var map_px := current_map.pixel_size()
	var target := player.position + Vector2(Game.TILE / 2.0, Game.TILE / 2.0)
	for axis in 2:
		if map_px[axis] <= view[axis]:
			target[axis] = map_px[axis] / 2.0
		else:
			target[axis] = clampf(target[axis], view[axis] / 2.0, map_px[axis] - view[axis] / 2.0)
	camera.position = target.round()


func _build_banner(ui: CanvasLayer) -> void:
	_banner = PanelContainer.new()
	_banner.name = "MapBanner"
	var s := StyleBoxFlat.new()
	s.bg_color = Color("#f4f1e8")
	s.border_color = Color("#1d1922")
	s.set_border_width_all(2)
	s.border_width_left = 0
	s.content_margin_left = 8
	s.content_margin_right = 8
	s.content_margin_top = 5
	s.content_margin_bottom = 4
	s.anti_aliasing = false
	_banner.add_theme_stylebox_override("panel", s)
	_banner_label = Label.new()
	_banner_label.add_theme_color_override("font_color", Color("#1d1922"))
	_banner_label.add_theme_font_size_override("font_size", 8)
	_banner.add_child(_banner_label)
	_banner.position = Vector2(0, 6)
	_banner.modulate.a = 0.0
	ui.add_child(_banner)


func _show_banner(text: String) -> void:
	_banner_label.text = text
	_banner.reset_size()
	if _banner_tween:
		_banner_tween.kill()
	_banner.position.x = -_banner.size.x
	_banner.modulate.a = 1.0
	_banner_tween = create_tween()
	_banner_tween.tween_interval(FADE_TIME)
	_banner_tween.tween_property(_banner, "position:x", 0.0, 0.2)
	_banner_tween.tween_interval(1.8)
	_banner_tween.tween_property(_banner, "position:x", -_banner.size.x, 0.2)
