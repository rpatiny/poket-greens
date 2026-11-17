extends Node2D
## Objeto parado no mapa: vaso, equipamento, placa, porta trancada...
## "prop" desenha camadas de objetos.png; "inspect" é invisível (placas, janelas, portão);
## "door" é invisível e também fala quando o jogador esbarra nela.

const OBJ_FRAME := 16

var cell := Vector2i.ZERO
var solid := true
var on_bump := false
var lines: Array = []
var speaker := ""

var _bobbing: Array[Sprite2D] = []


func setup(obj: Dictionary) -> void:
	var c: Array = obj["cell"]
	cell = Vector2i(int(c[0]), int(c[1]))
	position = Vector2(cell * Game.TILE)
	name = "Prop_%s_%d_%d" % [obj.get("id", obj.get("type")), cell.x, cell.y]
	lines = obj.get("dialog", [])
	speaker = obj.get("name", "")
	solid = obj.get("solid", true)
	on_bump = obj.get("type") == "door"
	var tex := Game.sprite("objetos")
	for layer in obj.get("layers", []):
		var s := Sprite2D.new()
		s.texture = tex
		s.centered = false
		s.region_enabled = true
		s.region_rect = Rect2(int(layer.get("frame", 0)) * OBJ_FRAME, 0, OBJ_FRAME, OBJ_FRAME)
		var off: Array = layer.get("offset", [0, 0])
		s.position = Vector2(off[0], off[1])
		add_child(s)
		if layer.get("bob", false):
			_bobbing.append(s)


func _ready() -> void:
	for s in _bobbing:
		var tw := s.create_tween().set_loops()
		tw.tween_property(s, "position:y", s.position.y - 2, 0.4).set_trans(Tween.TRANS_SINE)
		tw.tween_property(s, "position:y", s.position.y, 0.4).set_trans(Tween.TRANS_SINE)


func interact(_player: Node) -> void:
	if not lines.is_empty():
		await Game.say(lines, speaker)
