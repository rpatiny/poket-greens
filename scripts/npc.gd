extends Actor
## NPC: fala quando o jogador aperta ação na frente dele; pode passear dentro de uma área.

var id := ""
var speaker := ""
var lines: Array = []
var home_facing := Vector2i.DOWN
var wander_rect := Rect2i()  # vazio = fica parado

var _wander_timer := 0.0
var _rng := RandomNumberGenerator.new()


func setup(obj: Dictionary) -> void:
	id = obj.get("id", "")
	name = "Npc_" + id
	speaker = obj.get("name", "")
	lines = obj.get("dialog", [])
	home_facing = Game.DIRS.get(obj.get("facing", "down"), Vector2i.DOWN)
	if obj.has("wander"):
		var w: Array = obj["wander"]
		wander_rect = Rect2i(int(w[0]), int(w[1]), int(w[2]) - int(w[0]) + 1, int(w[3]) - int(w[1]) + 1)
	set_texture(Game.sprite(obj.get("sprite", "avatar")))
	var c: Array = obj["cell"]
	place(Vector2i(int(c[0]), int(c[1])), home_facing)
	_rng.seed = hash(id)
	_wander_timer = _rng.randf_range(1.0, 3.0)


func interact(player: Node) -> void:
	face(-player.facing)
	await Game.say(lines, speaker)
	if not wander_rect.has_area():
		face(home_facing)


func _process(delta: float) -> void:
	super(delta)
	if moving or not wander_rect.has_area() or Game.is_busy():
		return
	_wander_timer -= delta
	if _wander_timer > 0.0:
		return
	_wander_timer = _rng.randf_range(1.0, 3.0)
	var dirs := Game.DIRS.values()
	var dir: Vector2i = dirs[_rng.randi() % dirs.size()]
	if wander_rect.has_point(cell + dir):
		try_step(dir)
	else:
		face(dir)
