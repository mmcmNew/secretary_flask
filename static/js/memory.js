function closeMemory(memoryId) {
    let memoryContainer = $("#" + memoryId + "_memoryContainer");
    memoryContainer.remove();
    if ($("#toolsPanel").children().length === 0) {
        $('#toolsPanel').attr('hidden', true);
    }
}

$('#toolsPanel').on('click', '.closeMemory', function() {
    let memoryId = this.id.split('_')[0];
    closeMemory(memoryId);
});


