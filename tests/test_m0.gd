extends Node
## Testes do marco M0. Rodar:
##   godot --headless res://tests/test_m0.tscn
## Com "--shots <pasta>" (sem --headless, ex. via xvfb-run) também salva capturas de tela.

var _failures := 0
var _main: Node
var _shots_dir := ""


func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	var i := args.find("--shots")
	if i >= 0 and i + 1 < args.size():
		_shots_dir = args[i + 1]
	TranslationServer.set_locale("pt_BR")
	_run.call_deferred()


func _run() -> void:
	test_map_data()
	test_dialog_strings_fit()

	_main = load("res://scenes/main.tscn").instantiate()
	add_child(_main)
	await _frames(40)
	await _shot("01_garagem")
	await test_interact_pot()
	await _shot("02_dialogo")
	await _close_dialog()
	await test_walk_out_to_street()
	await _shot("03_rua")
	await test_blocked_and_bump()
	await test_talk_to_avo()
	await _shot("04_avo")
	await _close_dialog()
	await test_walk_back_inside()

	if _failures == 0:
		print("\nM0: TODOS OS TESTES PASSARAM")
	else:
		print("\nM0: %d FALHA(S)" % _failures)
	get_tree().quit(1 if _failures else 0)


# --- Testes de dados ------------------------------------------------------------

func test_map_data() -> void:
	var legend: Dictionary = Game.tile_db()["legend"]
	for file in DirAccess.get_files_at(Game.MAPS_DIR):
		if not file.ends_with(".json"):
			continue
		var id := file.get_basename()
		var data := Game.map_data(id)
		var rows: Array = data["ground"]
		var w := String(rows[0]).length()
		for y in rows.size():
			var row := String(rows[y])
			check(row.length() == w, "%s: linha %d com largura %d (esperado %d)" % [id, y, row.length(), w])
			for ch in row:
				check(legend.has(ch), "%s: caractere '%s' sem legenda" % [id, ch])
		for warp in data.get("warps", []):
			check(FileAccess.file_exists(Game.MAPS_DIR + warp["to"] + ".json"), "%s: portal para mapa inexistente %s" % [id, warp["to"]])
		check(tr(data["name"]) != data["name"], "%s: nome sem tradução" % id)
		for obj in data.get("objects", []):
			for key in obj.get("dialog", []):
				check(tr(key) != key, "%s: fala sem tradução %s" % [id, key])
	print("ok  dados dos mapas")


func test_dialog_strings_fit() -> void:
	# Toda fala precisa caber em 3 linhas da caixa em todos os idiomas.
	var box := DialogBox.new()
	add_child(box)
	var label: Label = box.find_children("*", "Label", true, false)[0]
	for locale in ["pt_BR", "en", "es"]:
		TranslationServer.set_locale(locale)
		var t: Translation = TranslationServer.get_translation_object(locale)
		for key in t.get_message_list():
			label.text = tr(key)
			check(label.get_line_count() <= 3, "[%s] %s não cabe na caixa (%d linhas)" % [locale, key, label.get_line_count()])
	TranslationServer.set_locale("pt_BR")
	box.queue_free()
	print("ok  falas cabem na caixa")


# --- Testes de jogo -------------------------------------------------------------

func test_interact_pot() -> void:
	var p: Player = _main.player
	check(_main.current_map.map_id == "garagem", "começa na garagem")
	check(p.cell == Vector2i(4, 5), "começa na célula (4,5), está em %s" % p.cell)
	# Andar até (3,4) e olhar para cima, para o vaso pronto em (3,3).
	await _walk("left", 1)
	await _walk("up", 1)
	await _tap("up")
	check(p.cell == Vector2i(3, 4), "parou na frente do vaso, está em %s" % p.cell)
	check(p.facing == Vector2i.UP, "olhando para cima")
	await _press_action()
	await _frames(60)
	check(_main.dialog.open, "apertar ação abre o diálogo")
	var label: Label = _main.dialog.find_children("*", "Label", true, false)[0]
	check(label.text == tr("POT_READY"), "fala do vaso: '%s'" % label.text)
	print("ok  interagir com o vaso")


func test_walk_out_to_street() -> void:
	var p: Player = _main.player
	await _walk("right", 1)
	await _walk("down", 3)
	check(p.cell == Vector2i(4, 7), "chegou no capacho, está em %s" % p.cell)
	await _walk("down", 1)  # sair pela borda de baixo
	await _frames(40)
	check(_main.current_map.map_id == "rua", "saiu para a rua (mapa: %s)" % _main.current_map.map_id)
	check(p.cell == Vector2i(7, 18), "apareceu na frente da garagem, está em %s" % p.cell)
	print("ok  sair da garagem para a rua")


func test_blocked_and_bump() -> void:
	var p: Player = _main.player
	# À esquerda de (7,18) há grama livre; abaixo há árvores (sólidas).
	await _walk("down", 2)
	check(p.cell == Vector2i(7, 18), "árvore bloqueia o caminho, está em %s" % p.cell)
	check(not _main.dialog.open, "esbarrar em árvore não abre diálogo")
	print("ok  colisão")


func test_talk_to_avo() -> void:
	var p: Player = _main.player
	# Da garagem até a Vó Dita em (6,7): pela coluna 1, que é livre de cima a baixo.
	await _walk("left", 6)    # (1,18)
	await _walk("up", 10)     # (1,8) calçada de cima
	await _walk("right", 5)   # (6,8)
	check(p.cell == Vector2i(6, 8), "chegou embaixo da Vó, está em %s" % p.cell)
	await _tap("up")
	await _press_action()
	await _frames(90)
	check(_main.dialog.open, "falar com a Vó abre o diálogo")
	var avo: Node = _main.current_map.entities.get_node("Npc_avo")
	check(avo.facing == Vector2i.DOWN, "a Vó vira para o jogador")
	print("ok  conversar com NPC")


func test_walk_back_inside() -> void:
	var p: Player = _main.player
	await _walk("left", 5)    # (1,8)
	await _walk("down", 10)   # (1,18)
	await _walk("right", 6)   # (7,18)
	await _walk("up", 1)      # entra pela porta em (7,17)
	await _frames(40)
	check(_main.current_map.map_id == "garagem", "voltou para a garagem (mapa: %s)" % _main.current_map.map_id)
	check(p.cell == Vector2i(4, 7) and p.facing == Vector2i.UP, "aparece no capacho olhando para cima (%s)" % p.cell)
	print("ok  entrar na garagem pela porta")


# --- Utilitários -----------------------------------------------------------------

func check(cond: bool, msg: String) -> void:
	if not cond:
		_failures += 1
		push_error("FALHOU: " + msg)
		print("FALHOU: " + msg)


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


## Segura a direção até o jogador dar n passos (ou desistir se estiver bloqueado).
func _walk(dir: String, steps: int) -> void:
	var p: Player = _main.player
	for s in steps:
		var before: Vector2i = p.cell
		var map_before: String = _main.current_map.map_id
		Input.action_press("move_" + dir)
		var waited := 0
		while waited < 60 and p.cell == before and _main.current_map.map_id == map_before:
			await get_tree().process_frame
			waited += 1
		Input.action_release("move_" + dir)
		while p.moving or _main.is_busy():
			await get_tree().process_frame
		await _frames(2)


func _tap(dir: String) -> void:
	Input.action_press("move_" + dir)
	await _frames(2)
	Input.action_release("move_" + dir)
	await _frames(2)


func _press_action() -> void:
	Input.action_press("action")
	await _frames(1)
	Input.action_release("action")
	await _frames(1)


func _close_dialog() -> void:
	var guard := 0
	while _main.dialog.open and guard < 20:
		await _press_action()
		await _frames(3)
		guard += 1
	check(not _main.dialog.open, "diálogo fecha")


func _shot(name: String) -> void:
	if _shots_dir == "":
		return
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.save_png(_shots_dir.path_join(name + ".png"))
