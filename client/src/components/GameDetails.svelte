<script lang="ts">
    import { onMount } from "svelte";
    
    interface Game {
        id: number;
        title: string;
        description: string;
        publisher: {
            id: number;
            name: string;
        } | null;
        category: {
            id: number;
            name: string;
        } | null;
        starRating: number | null;
    }

    // Accept either a game object or a gameId
    export let game: Game | undefined = undefined;
    export let gameId = 0;
    
    let loading = true;
    let error: string | null = null;
    let gameData: Game | null = null;
    
    onMount(async () => {
        // If game object is provided directly, use it
        if (game) {
            gameData = game;
            loading = false;
            return;
        }
        
        // Otherwise fetch data using gameId
        if (gameId) {
            try {
                const response = await fetch(`/api/games/${gameId}`);
                if (response.ok) {
                    gameData = await response.json();
                } else {
                    error = `Failed to fetch game: ${response.status} ${response.statusText}`;
                }
            } catch (err) {
                error = `Error: ${err instanceof Error ? err.message : String(err)}`;
            } finally {
                loading = false;
            }
        } else {
            error = "No game ID provided";
            loading = false;
        }
    });

    // Function to render stars based on rating
    function renderStarRating(rating: number | null): string {
        if (rating === null) return "Not yet rated";
        
        const fullStars = Math.floor(rating);
        const halfStar = rating % 1 >= 0.5;
        const emptyStars = 5 - fullStars - (halfStar ? 1 : 0);
        
        return '★'.repeat(fullStars) + (halfStar ? '½' : '') + '☆'.repeat(emptyStars);
    }
</script>

{#if loading}
    <div class="animate-pulse bg-slate-800/60 backdrop-blur-sm rounded-xl overflow-hidden">
        <div class="h-1 bg-slate-700 w-full"></div>
        <div class="p-8">
            <div class="h-8 bg-slate-700 rounded-lg w-1/2 mb-6"></div>
            <div class="flex gap-2 mb-6">
                <div class="h-6 bg-slate-700 rounded-full w-24"></div>
                <div class="h-6 bg-slate-700 rounded-full w-20"></div>
            </div>
            <div class="h-4 bg-slate-700 rounded w-full mb-2"></div>
            <div class="h-4 bg-slate-700 rounded w-5/6 mb-2"></div>
            <div class="h-4 bg-slate-700 rounded w-4/6 mb-8"></div>
            <div class="h-12 bg-slate-700 rounded-xl w-full"></div>
        </div>
    </div>
{:else if error}
    <div class="bg-red-500/10 border border-red-500/40 text-red-400 rounded-xl p-8 flex items-start gap-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <span>{error}</span>
    </div>
{:else if gameData}
    <div class="bg-slate-800/70 backdrop-blur-sm border border-slate-700 rounded-xl overflow-hidden shadow-xl" data-testid="game-details">

        <!-- Gradient accent bar -->
        <div class="h-1.5 w-full bg-gradient-to-r from-blue-500 to-purple-500"></div>

        <div class="p-8">
            <!-- Title row -->
            <div class="flex justify-between items-start flex-wrap gap-4 mb-5">
                <h1 class="text-3xl font-bold text-slate-100 leading-tight" data-testid="game-details-title">{gameData.title}</h1>

                {#if gameData.starRating !== null}
                    <div class="shrink-0" data-testid="game-rating">
                        <span class="inline-flex items-center gap-2 bg-yellow-400/10 border border-yellow-400/30 text-yellow-400 text-sm px-3 py-1.5 rounded-full font-medium">
                            <span>{renderStarRating(gameData.starRating)}</span>
                            <span class="text-yellow-300 font-semibold">{gameData.starRating.toFixed(1)}</span>
                        </span>
                    </div>
                {/if}
            </div>

            <!-- Badges -->
            <div class="flex flex-wrap gap-2 mb-8">
                {#if gameData.category}
                    <span class="inline-flex items-center text-xs font-medium px-3 py-1 rounded-full bg-blue-900/60 text-blue-300 border border-blue-700/30" data-testid="game-details-category">
                        {gameData.category.name}
                    </span>
                {/if}
                {#if gameData.publisher}
                    <span class="inline-flex items-center text-xs font-medium px-3 py-1 rounded-full bg-purple-900/60 text-purple-300 border border-purple-700/30" data-testid="game-details-publisher">
                        {gameData.publisher.name}
                    </span>
                {/if}
            </div>

            <!-- Divider -->
            <div class="border-t border-slate-700/60 mb-8"></div>

            <!-- Description -->
            <div class="mb-10">
                <h2 class="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">About this game</h2>
                <p class="text-slate-300 leading-relaxed" data-testid="game-details-description">{gameData.description}</p>
            </div>

            <!-- Support button -->
            <button
                class="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-semibold py-3.5 px-4 rounded-xl transition-all duration-200 flex justify-center items-center gap-2 shadow-lg shadow-blue-500/20 hover:shadow-blue-500/30 hover:-translate-y-px"
                data-testid="back-game-button"
            >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clip-rule="evenodd" />
                </svg>
                Support This Game
            </button>
        </div>
    </div>
{:else}
    <div class="bg-slate-800/60 backdrop-blur-sm rounded-xl p-8 text-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-slate-600 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="text-slate-400 font-medium">No game information available</p>
    </div>
{/if}