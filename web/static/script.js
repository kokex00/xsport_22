// Translation data
const translations = {
    es: {
        hero_title: "Bot de Gestión para xSportBS",
        hero_description: "Un potente bot multilingüe diseñado para la gestión del servidor y protección. Con sistema completo de gestión de partidos y herramientas administrativas.",
        servers: "Servidores",
        users: "Usuarios",
        online: "En Línea",
        status: "Estado",
        features_title: "Características Principales",
        features_description: "Descubre todas las funcionalidades que ofrece xSportBS",
        feature_matches: "Gestión de Partidos",
        feature_matches_desc: "Sistema completo para crear, gestionar y programar partidos con recordatorios automáticos.",
        feature_protection: "Protección del Servidor",
        feature_protection_desc: "Herramientas avanzadas de administración y control de canales para mantener tu servidor seguro.",
        feature_multilingual: "Multilingüe",
        feature_multilingual_desc: "Soporte completo para español, inglés y portugués con conversión automática de zonas horarias.",
        commands_title: "Comandos Disponibles",
        commands_description: "Lista completa de comandos slash disponibles",
        match_commands: "Comandos de Partidos",
        admin_commands: "Comandos de Administración",
        general_commands: "Comandos Generales",
        cmd_creatematch: "Crear un nuevo partido con equipos, fecha, hora e imagen",
        cmd_endmatch: "Terminar un partido activo",
        cmd_listmatches: "Mostrar todos los partidos activos",
        cmd_setlogchannel: "Establecer canal para registros de actividad",
        cmd_setchannels: "Establecer canales permitidos para el bot",
        cmd_dmuser: "Enviar mensaje directo a un usuario",
        cmd_dmrole: "Enviar mensaje directo a un rol",
        cmd_customembed: "Enviar embed personalizado con imagen",
        cmd_help: "Mostrar ayuda y todos los comandos disponibles",
        support_title: "Soporte Técnico",
        support_description: "Nuestro equipo está aquí para ayudarte",
        join_server: "Únete al Servidor",
        footer_text: "xSportBS Bot - Sistema de gestión para servidores de Discord"
    },
    en: {
        hero_title: "Management Bot for xSportBS",
        hero_description: "A powerful multilingual bot designed for server management and protection. With complete match management system and administrative tools.",
        servers: "Servers",
        users: "Users",
        online: "Online",
        status: "Status",
        features_title: "Main Features",
        features_description: "Discover all the functionalities that xSportBS offers",
        feature_matches: "Match Management",
        feature_matches_desc: "Complete system to create, manage and schedule matches with automatic reminders.",
        feature_protection: "Server Protection",
        feature_protection_desc: "Advanced administration tools and channel control to keep your server secure.",
        feature_multilingual: "Multilingual",
        feature_multilingual_desc: "Full support for Spanish, English and Portuguese with automatic timezone conversion.",
        commands_title: "Available Commands",
        commands_description: "Complete list of available slash commands",
        match_commands: "Match Commands",
        admin_commands: "Administration Commands",
        general_commands: "General Commands",
        cmd_creatematch: "Create a new match with teams, date, time and image",
        cmd_endmatch: "End an active match",
        cmd_listmatches: "Show all active matches",
        cmd_setlogchannel: "Set channel for activity logs",
        cmd_setchannels: "Set allowed channels for the bot",
        cmd_dmuser: "Send direct message to a user",
        cmd_dmrole: "Send direct message to a role",
        cmd_customembed: "Send custom embed with image",
        cmd_help: "Show help and all available commands",
        support_title: "Technical Support",
        support_description: "Our team is here to help you",
        join_server: "Join Server",
        footer_text: "xSportBS Bot - Management system for Discord servers"
    },
    pt: {
        hero_title: "Bot de Gestão para xSportBS",
        hero_description: "Um poderoso bot multilíngue projetado para gestão e proteção de servidor. Com sistema completo de gestão de partidas e ferramentas administrativas.",
        servers: "Servidores",
        users: "Utilizadores",
        online: "Online",
        status: "Estado",
        features_title: "Características Principais",
        features_description: "Descubra todas as funcionalidades que o xSportBS oferece",
        feature_matches: "Gestão de Partidas",
        feature_matches_desc: "Sistema completo para criar, gerir e agendar partidas com lembretes automáticos.",
        feature_protection: "Proteção do Servidor",
        feature_protection_desc: "Ferramentas avançadas de administração e controlo de canais para manter o servidor seguro.",
        feature_multilingual: "Multilíngue",
        feature_multilingual_desc: "Suporte completo para espanhol, inglês e português com conversão automática de fuso horário.",
        commands_title: "Comandos Disponíveis",
        commands_description: "Lista completa de comandos slash disponíveis",
        match_commands: "Comandos de Partidas",
        admin_commands: "Comandos de Administração",
        general_commands: "Comandos Gerais",
        cmd_creatematch: "Criar uma nova partida com equipas, data, hora e imagem",
        cmd_endmatch: "Terminar uma partida ativa",
        cmd_listmatches: "Mostrar todas as partidas ativas",
        cmd_setlogchannel: "Definir canal para registos de atividade",
        cmd_setchannels: "Definir canais permitidos para o bot",
        cmd_dmuser: "Enviar mensagem direta a um utilizador",
        cmd_dmrole: "Enviar mensagem direta a um cargo",
        cmd_customembed: "Enviar embed personalizado com imagem",
        cmd_help: "Mostrar ajuda e todos os comandos disponíveis",
        support_title: "Suporte Técnico",
        support_description: "A nossa equipa está aqui para ajudar",
        join_server: "Juntar-se ao Servidor",
        footer_text: "xSportBS Bot - Sistema de gestão para servidores Discord"
    }
};

// Current language
let currentLanguage = 'es';

// Language switching function
function switchLanguage(lang) {
    if (!translations[lang]) return;
    
    currentLanguage = lang;
    
    // Update language buttons
    document.querySelectorAll('.language-switcher .btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.getElementById(`lang-${lang}`).classList.add('active');
    
    // Update all translatable elements
    document.querySelectorAll('[data-translate]').forEach(element => {
        const key = element.getAttribute('data-translate');
        if (translations[lang][key]) {
            element.textContent = translations[lang][key];
        }
    });
    
    // Update HTML lang attribute
    document.documentElement.lang = lang;
    
    // Save language preference
    localStorage.setItem('preferredLanguage', lang);
}

// Load stats from API
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        if (!data.error) {
            document.getElementById('guild-count').textContent = data.guilds || '-';
            document.getElementById('user-count').textContent = data.users || '-';
        }
    } catch (error) {
        console.warn('Could not load stats:', error);
    }
}

// Initialize page
function initializePage() {
    // Load saved language or default to Spanish
    const savedLanguage = localStorage.getItem('preferredLanguage') || 'es';
    switchLanguage(savedLanguage);
    
    // Load stats
    loadStats();
    
    // Set up periodic stats refresh
    setInterval(loadStats, 30000); // Refresh every 30 seconds
    
    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add loading animation for external links
    document.querySelectorAll('a[target="_blank"]').forEach(link => {
        link.addEventListener('click', function() {
            this.style.opacity = '0.6';
            setTimeout(() => {
                this.style.opacity = '1';
            }, 1000);
        });
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializePage);

// Add some interactive effects
document.addEventListener('DOMContentLoaded', function() {
    // Intersection Observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    document.querySelectorAll('.feature-card, .command-category, .support-member').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
});
