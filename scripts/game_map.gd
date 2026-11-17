class_name GameMap
extends Node2D
## Um mapa montado a partir de data/maps/<id>.json.
## Camadas: chão (TileMapLayer), sobreposição (TileMapLayer) e entidades ordenadas por Y.

const NpcScript := preload("res://scripts/npc.gd")
const PropScript := preload("res://scripts/prop.gd")

var map_id := ""
var data: Dictionary = {}
var size := Vector2i.ZERO
var entities: Node2D

var _solid: Dictionary = {}  # Vector2i -> true
var _ground: TileMapLayer
var _overlay: TileMapLayer


func setup(id: String) -> void:
	map_id = id
	name = "Map_" + id
	data = Game.map_data(id)
	var rows: Array = data.get("ground", [])
	size = Vector2i(String(rows[0]).length() if rows.size() > 0 else 0, rows.size())

	_ground = TileMapLayer.new()
	_ground.name = "Ground"
	_ground.tile_set = Game.tile_set()
	add_child(_ground)
	_overlay = TileMapLayer.new()
	_overlay.name = "Overlay"
	_overlay.tile_set = Game.tile_set()
	add_child(_overlay)

	var legend: Dictionary = Game.tile_db()["legend"]
	for y in rows.size():
		var row := String(rows[y])
		for x in row.length():
			var ch := row[x]
			var cell := Vector2i(x, y)
			if not legend.has(ch):
				push_error("%s: caractere '%s' sem legenda em %s" % [id, ch, cell])
				continue
			var def: Dictionary = legend[ch]
			if def.get("solid", false):
				_solid[cell] = true
			if def.has("under"):
				_paint(_ground, cell, legend[def["under"]])
				_paint(_overlay, cell, def)
			else:
				_paint(_ground, cell, def)

	entities = Node2D.new()
	entities.name = "Entities"
	entities.y_sort_enabled = true
	add_child(entities)
	for obj in data.get("objects", []):
		_spawn(obj)


func _paint(layer: TileMapLayer, cell: Vector2i, def: Dictionary) -> void:
	if not def.has("tex"):
		return
	var at: Array
	if def.has("variants"):
		var variants: Array = def["variants"]
		at = variants[absi(cell.x * 73856093 ^ cell.y * 19349663) % variants.size()]
	else:
		at = def["at"]
	layer.set_cell(cell, Game.source_id(def["tex"]), Vector2i(at[0], at[1]))


func _spawn(obj: Dictionary) -> void:
	var node: Node2D
	match obj.get("type", ""):
		"npc":
			node = NpcScript.new()
		"prop", "inspect", "door":
			node = PropScript.new()
		_:
			push_error("%s: tipo de objeto desconhecido %s" % [map_id, obj])
			return
	node.setup(obj)
	entities.add_child(node)


func add_entity(node: Node2D) -> void:
	entities.add_child(node)


func in_bounds(cell: Vector2i) -> bool:
	return cell.x >= 0 and cell.y >= 0 and cell.x < size.x and cell.y < size.y


func entity_at(cell: Vector2i, ignore: Node = null) -> Node:
	for e in entities.get_children():
		if e != ignore and e.get("cell") == cell:
			return e
	return null


## Uma célula está bloqueada se é fora do mapa, um tile sólido ou tem uma entidade sólida.
func is_blocked(cell: Vector2i, ignore: Node = null) -> bool:
	if not in_bounds(cell) or _solid.has(cell):
		return true
	var e := entity_at(cell, ignore)
	return e != null and e.get("solid") == true


## Portal disparado ao pisar na célula (sem "dir").
func step_warp(cell: Vector2i) -> Dictionary:
	for w in data.get("warps", []):
		if not w.has("dir") and _v(w["cell"]) == cell:
			return w
	return {}


## Portal disparado ao andar numa direção a partir da célula (ex.: sair pelo capacho).
func edge_warp(cell: Vector2i, dir: Vector2i) -> Dictionary:
	for w in data.get("warps", []):
		if w.has("dir") and _v(w["cell"]) == cell and Game.DIRS[w["dir"]] == dir:
			return w
	return {}


func pixel_size() -> Vector2:
	return Vector2(size * Game.TILE)


static func _v(a: Array) -> Vector2i:
	return Vector2i(int(a[0]), int(a[1]))
