<script lang="ts">
    import '../app.css';
    let { children } = $props();
</script>

<main>
    {@render children()}
</main>

<style>
    main {
        display: flex;
        min-height: 100vh;
        align-items: center;
        justify-content: center;
    }
</style>
