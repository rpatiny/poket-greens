class_name DialogBox
extends Control
## Caixa de diálogo estilo RPG de portátil: embaixo da tela, texto letra por letra,
## setinha piscando quando a fala terminou. Ação acelera o texto ou passa para a próxima fala.

signal finished

const CHARS_PER_SEC := 45.0
const INK := Color("#1d1922")
const PAPER := Color("#f4f1e8")
const EDGE := Color("#93a0b0")

var open := false

var _lines: Array = []
var _index := 0
var _shown := 0.0
var _label: Label
var _name_tag: PanelContainer
var _name_label: Label
var _arrow: Polygon2D
var _blink := 0.0


func _init() -> void:
	name = "DialogBox"
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	visible = false

	var box := Panel.new()
	box.position = Vector2(4, 128)
	box.size = Vector2(312, 48)
	box.add_theme_stylebox_override("panel", _style(PAPER))
	add_child(box)

	_label = Label.new()
	_label.position = Vector2(10, 8)
	_label.size = Vector2(292, 34)
	_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_label.add_theme_color_override("font_color", INK)
	_label.add_theme_font_size_override("font_size", 8)
	_label.add_theme_constant_override("line_spacing", 4)
	_label.visible_characters_behavior = TextServer.VC_CHARS_AFTER_SHAPING
	box.add_child(_label)

	_arrow = Polygon2D.new()
	_arrow.polygon = PackedVector2Array([Vector2(0, 0), Vector2(6, 0), Vector2(3, 3)])
	_arrow.color = INK
	_arrow.position = Vector2(300, 40)
	box.add_child(_arrow)

	_name_tag = PanelContainer.new()
	_name_tag.position = Vector2(4, 114)
	var tag_style := _style(PAPER)
	tag_style.content_margin_left = 6
	tag_style.content_margin_right = 6
	tag_style.content_margin_top = 3
	tag_style.content_margin_bottom = 2
	_name_tag.add_theme_stylebox_override("panel", tag_style)
	add_child(_name_tag)
	_name_label = Label.new()
	_name_label.add_theme_color_override("font_color", Color("#8f2f3d"))
	_name_label.add_theme_font_size_override("font_size", 8)
	_name_tag.add_child(_name_label)


func _style(bg: Color) -> StyleBoxFlat:
	var s := StyleBoxFlat.new()
	s.bg_color = bg
	s.border_color = INK
	s.set_border_width_all(2)
	s.set_corner_radius_all(3)
	s.shadow_color = EDGE
	s.shadow_size = 0
	s.anti_aliasing = false
	return s


## Abre o diálogo com uma lista de chaves de tradução. Espere o sinal "finished".
func show_lines(lines: Array, speaker := "") -> void:
	_lines = lines
	_index = 0
	open = true
	visible = true
	_name_tag.visible = speaker != ""
	_name_label.text = tr(speaker) if speaker != "" else ""
	_start_line()


func _start_line() -> void:
	_label.text = tr(String(_lines[_index]))
	_shown = 0.0
	_label.visible_characters = 0
	_arrow.visible = false


func is_line_complete() -> bool:
	return _label.visible_characters < 0 or _label.visible_characters >= _label.get_total_character_count()


func _process(delta: float) -> void:
	if not open:
		return
	if not is_line_complete():
		var speed := CHARS_PER_SEC * (3.0 if Input.is_action_pressed("run") else 1.0)
		_shown += delta * speed
		_label.visible_characters = int(_shown)
	else:
		_blink += delta
		_arrow.visible = fmod(_blink, 0.6) < 0.4
		_arrow.position.y = 40 + (1 if fmod(_blink, 0.6) < 0.3 else 0)

	if Game.action_pressed():
		Game.consume_action()
		advance()


## Completa a fala atual ou passa para a próxima. Fecha depois da última.
func advance() -> void:
	if not is_line_complete():
		_label.visible_characters = -1
		return
	_index += 1
	if _index < _lines.size():
		_start_line()
	else:
		open = false
		visible = false
		finished.emit()
